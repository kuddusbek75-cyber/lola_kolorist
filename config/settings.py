import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env_list(name):
    return [v.strip() for v in os.getenv(name, '').split(',') if v.strip()]


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

INSTALLED_APPS = [
    'salon',  # первым: переопределяет команду runserver
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'salon.context.salon_info',
    ]},
}]

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Telegram CRM bot
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')

# Salon info
SALON_NAME = 'LK beauty studio'
SALON_ADDRESS = 'Эне-Сай, ул. Токтогула, 51'
SALON_INSTAGRAM = 'https://www.instagram.com/lk_beauty_studio_mns/'
SALON_PHONE = os.getenv('SALON_PHONE', '')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
