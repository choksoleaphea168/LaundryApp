import json
import logging
import httpx
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings

from .services import (
    send_telegram_message,
    register_or_update_recipient,
    get_all_recipient_chat_ids
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Receives incoming webhook events from Telegram Bot API:
    https://core.telegram.org/bots/api#update
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponse("Bad Request", status=400)

        message = data.get('message') or data.get('edited_message') or data.get('channel_post')
        if not message:
            return JsonResponse({'ok': True, 'note': 'No message object'})

        chat = message.get('chat', {})
        chat_id = chat.get('id')
        user = message.get('from', {})
        first_name = user.get('first_name') or chat.get('title') or "User"
        username = user.get('username') or ""
        text = (message.get('text') or "").strip()

        if chat_id:
            # Register or update recipient
            register_or_update_recipient(
                chat_id=str(chat_id),
                first_name=first_name,
                username=username
            )

            # Auto-reply for commands
            if text.startswith('/start') or text.startswith('/id') or text.startswith('/help') or 'hello' in text.lower() or 'សួស្តី' in text:
                welcome_reply = (
                    f"👋 <b>សួស្តី {first_name}!</b>\n\n"
                    f"Telegram Bot <b>@VeasnaKafebot</b> ត្រូវបានតភ្ជាប់ជាមួយប្រព័ន្ធ <b>ស្អាតជានិច្ច Laundry POS</b> ដោយជោគជ័យ! 🎉\n\n"
                    f"📌 <b>Telegram Chat ID របស់អ្នកគឺ:</b> <code>{chat_id}</code>\n\n"
                    f"🔔 <b>ប្រព័ន្ធបានកំណត់ទទួលការជូនដំណឹងស្វ័យប្រវត្តិ៖</b>\n"
                    f"  1. 🧺 ការកក់បោកអ៊ុតថ្មី (New Orders)\n"
                    f"  2. 💰 ការទូទាត់ប្រាក់ (Payments)\n"
                    f"  3. ✅ ខោអាវរួចរាល់រង់ចាំយក (Ready for Pickup)\n\n"
                    f"<i>ប្រព័ន្ធនឹងផ្ញើសារជូនដំណឹងដោយស្វ័យប្រវត្តិនូវរាល់សកម្មភាពខាងលើ។</i>"
                )
                send_telegram_message(str(chat_id), welcome_reply)
            elif text.startswith('/status') or text.startswith('/ping'):
                status_reply = (
                    f"⚡ <b>ប្រព័ន្ធដំណើរការប្រក្រតី (System Online)</b>\n"
                    f"• Bot: @VeasnaKafebot\n"
                    f"• Chat ID: <code>{chat_id}</code>\n"
                    f"• ហាង: ស្អាតជានិច្ច Laundry"
                )
                send_telegram_message(str(chat_id), status_reply)

        return JsonResponse({'ok': True})

    def get(self, request, *args, **kwargs):
        """Simple healthcheck / status for the telegram endpoint."""
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        has_token = bool(token)
        masked_token = token[:10] + "..." + token[-6:] if has_token else "NOT SET"
        recipients = get_all_recipient_chat_ids()
        return JsonResponse({
            'ok': True,
            'bot_configured': has_token,
            'token_preview': masked_token,
            'registered_recipients_count': len(recipients),
            'recipients': recipients,
        })


def sync_telegram_updates(request):
    """
    Manually pulls updates from Telegram API via getUpdates
    and registers any user who sent a message to the bot.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not bot_token:
        return JsonResponse({'ok': False, 'error': 'TELEGRAM_BOT_TOKEN is not configured'}, status=400)

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(url)
            data = resp.json()
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    if not data.get('ok'):
        return JsonResponse({'ok': False, 'telegram_error': data})

    results = data.get('result', [])
    new_users = []
    for item in results:
        msg = item.get('message') or item.get('channel_post')
        if not msg:
            continue
        chat = msg.get('chat', {})
        chat_id = chat.get('id')
        user = msg.get('from', {})
        first_name = user.get('first_name') or chat.get('title') or ""
        username = user.get('username') or ""
        if chat_id:
            register_or_update_recipient(str(chat_id), first_name, username)
            new_users.append({
                'chat_id': str(chat_id),
                'first_name': first_name,
                'username': username
            })

    return JsonResponse({
        'ok': True,
        'updates_found': len(results),
        'registered_users': new_users,
        'all_active_recipients': get_all_recipient_chat_ids()
    })
