import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .bot_handlers import process_update

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def telegram_webhook(request):
    secret = settings.TELEGRAM_WEBHOOK_SECRET
    got = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    if not secret or not hmac.compare_digest(got.encode(), secret.encode()):
        return HttpResponseForbidden()
    try:
        process_update(json.loads(request.body))
    except Exception:
        logger.exception('Ошибка обработки webhook')
    return HttpResponse('ok')