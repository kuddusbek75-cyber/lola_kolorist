from django.conf import settings


def salon_info(request):
    return {
        'SALON_NAME': settings.SALON_NAME,
        'SALON_ADDRESS': settings.SALON_ADDRESS,
        'SALON_PHONE': settings.SALON_PHONE,
        'SALON_INSTAGRAM': settings.SALON_INSTAGRAM,
    }
