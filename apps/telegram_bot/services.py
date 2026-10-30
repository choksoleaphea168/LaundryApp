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
        'chat_id': str(chat_id),
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


def get_all_recipient_chat_ids() -> list:
    """Returns a unique list of active Telegram chat IDs."""
    chat_ids = set()
    env_chat_id = getattr(settings, 'TELEGRAM_OWNER_CHAT_ID', '')
    if env_chat_id:
        chat_ids.add(str(env_chat_id).strip())

    try:
        from .models import TelegramRecipient
        db_chat_ids = TelegramRecipient.objects.filter(is_active=True).values_list('chat_id', flat=True)
        for cid in db_chat_ids:
            if cid:
                chat_ids.add(str(cid).strip())
    except Exception as e:
        logger.debug(f"Could not load recipients from DB: {e}")

    return list(chat_ids)


def register_or_update_recipient(chat_id: str, first_name: str = "", username: str = ""):
    """Registers or activates a chat_id in the database."""
    try:
        from .models import TelegramRecipient
        recipient, created = TelegramRecipient.objects.update_or_create(
            chat_id=str(chat_id),
            defaults={
                'first_name': first_name or "",
                'username': username or "",
                'is_active': True,
            }
        )
        return recipient
    except Exception as e:
        logger.error(f"Error registering recipient {chat_id}: {e}")
        return None


def broadcast_message_to_recipients(message: str) -> int:
    """Broadcasts a message to all registered recipients and returns the success count."""
    chat_ids = get_all_recipient_chat_ids()
    sent_count = 0
    for cid in chat_ids:
        if send_telegram_message(cid, message):
            sent_count += 1
    return sent_count


def notify_owner_new_order(order):
    """Notify store owner about a newly registered laundry order."""
    chat_ids = get_all_recipient_chat_ids()
    if not chat_ids:
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
    for cid in chat_ids:
        send_telegram_message(cid, msg)


def notify_owner_payment_received(order, amount_usd, method):
    """Notify store owner when payment is recorded."""
    chat_ids = get_all_recipient_chat_ids()
    if not chat_ids:
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
    for cid in chat_ids:
        send_telegram_message(cid, msg)


def notify_customer_order_ready(order):
    """Notify owner & customer when laundry order is ready for pickup."""
    chat_ids = get_all_recipient_chat_ids()
    if not chat_ids:
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
    for cid in chat_ids:
        send_telegram_message(cid, msg)
