import logging
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: str, message: str) -> bool:
    """
    Sends an outbound message to a Telegram chat or group.
    Fails safely if internet is unavailable or bot token is unconfigured.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not bot_token or not chat_id:
        logger.debug("Telegram notifications skipped: TELEGRAM_BOT_TOKEN or chat_id not set.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return True
            else:
                logger.warning(f"Telegram API error {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.warning(f"Failed to send Telegram notification: {e}")
        return False


def notify_owner_new_order(order):
    """Notify store owner about a newly registered laundry order."""
    owner_chat_id = getattr(settings, 'TELEGRAM_OWNER_CHAT_ID', '')
    if not owner_chat_id:
        return

    items_list = ""
    for item in order.items.all():
        unit = "kg" if item.service.unit_type == 'PER_KG' else "pcs"
        items_list += f"  • {item.service.name}: {item.quantity}{unit} (${item.subtotal_usd:.2f} / {item.subtotal_khr:,}៛)\n"

    express_tag = " ⚡ [EXPRESS]" if order.is_express else ""
    msg = (
        f"🧺 <b>ការកុម្ម៉ង់បោកអ៊ុតថ្មី / NEW LAUNDRY ORDER{express_tag}</b>\n\n"
        f"<b>កូដកញ្ចប់ (Order):</b> <code>{order.order_code}</code>\n"
        f"<b>អតិថិជន (Customer):</b> {order.customer.name} (☎️ {order.customer.phone})\n"
        f"<b>ចំនួនស្បោង (Bags):</b> {order.bag_count}\n"
        f"<b>ទំនិញ (Items):</b>\n{items_list}\n"
        f"<b>សរុប (Total):</b> <b>${order.total_usd:.2f}</b> ({order.total_khr:,} ៛)\n"
        f"<b>ស្ថានភាពទូទាត់:</b> {order.get_payment_status_display()}\n"
        f"<b>ស្ថានភាព:</b> {order.get_status_display()}"
    )
    send_telegram_message(owner_chat_id, msg)


def notify_owner_payment_received(order, amount_usd, method):
    """Notify store owner when payment is recorded."""
    owner_chat_id = getattr(settings, 'TELEGRAM_OWNER_CHAT_ID', '')
    if not owner_chat_id:
        return

    amount_khr = int(amount_usd * order.exchange_rate)
    msg = (
        f"💰 <b>បានទទួលការទូទាត់ប្រាក់ / PAYMENT RECEIVED</b>\n\n"
        f"<b>កូដកញ្ចប់ (Order):</b> <code>{order.order_code}</code>\n"
        f"<b>អតិថិជន:</b> {order.customer.name}\n"
        f"<b>ទឹកប្រាក់:</b> <b>${amount_usd:.2f}</b> ({amount_khr:,} ៛)\n"
        f"<b>វិធីទូទាត់:</b> {method}\n"
        f"<b>នៅខ្វះ (Balance Due):</b> ${order.balance_due_usd:.2f} ({order.balance_due_khr:,} ៛)\n"
        f"<b>ស្ថានភាពបច្ចុប្បន្ន:</b> {order.get_payment_status_display()}"
    )
    send_telegram_message(owner_chat_id, msg)


def notify_customer_order_ready(order):
    """Notify owner & optionally customer when laundry order is ready for pickup."""
    owner_chat_id = getattr(settings, 'TELEGRAM_OWNER_CHAT_ID', '')
    if not owner_chat_id:
        return

    msg = (
        f"✅ <b>ខោអាវរួចរាល់អាចមកយកបាន / LAUNDRY READY FOR PICKUP</b>\n\n"
        f"<b>កូដកញ្ចប់ (Order):</b> <code>{order.order_code}</code>\n"
        f"<b>អតិថិជន:</b> {order.customer.name} (☎️ {order.customer.phone})\n"
        f"<b>ចំនួនស្បោង:</b> {order.bag_count} កញ្ចប់\n"
        f"<b>ស្ថានភាពបង់ប្រាក់:</b> {order.get_payment_status_display()}\n"
        f"<b>នៅខ្វះ:</b> ${order.balance_due_usd:.2f} ({order.balance_due_khr:,} ៛)\n"
        f"សូមរៀបចំទុកដាក់ជូនអតិថិជន!"
    )
    send_telegram_message(owner_chat_id, msg)
