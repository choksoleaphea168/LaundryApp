"""
Django settings for LaundryApp project.
Configured for Local Web App with PostgreSQL / SQLite,
Thermal Receipt & Tag Printing, Kanban Board POS, Dual Currency (USD & KHR),
and Telegram Outbound Notifications.
"""

from pathlib import Path
import os
from decimal import Decimal
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-local-laundry-app-secret-key-replace-in-production'
)

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,.vercel.app').split(',')
    if host.strip()
]
if DEBUG:
    ALLOWED_HOSTS += ['testserver', '*']

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://*.vercel.app').split(',')
    if origin.strip()
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Custom Modular Apps
    'apps.accounts',
    'apps.services',
    'apps.orders',
    'apps.pos',
    'apps.telegram_bot',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.currency_and_shop_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database Configuration (Local PostgreSQL or Supabase PostgreSQL)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and ('localhost' in DATABASE_URL or '127.0.0.1' in DATABASE_URL or 'postgres' in DATABASE_URL or 'supabase' in DATABASE_URL):
    is_local = 'localhost' in DATABASE_URL or '127.0.0.1' in DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600 if is_local else 0,
            ssl_require=False if is_local else True,
        )
    }
    if not is_local:
        DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Phnom_Penh'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/pos/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ==============================================================================
# Laundry Shop Configuration (Cambodia POS)
# ==============================================================================
SHOP_NAME = os.getenv('SHOP_NAME', 'Smart Clean Laundry')
SHOP_NAME_KH = os.getenv('SHOP_NAME_KH', 'ហាងបោកអ៊ុត ស្មាតឃ្លីន')
SHOP_PHONE = os.getenv('SHOP_PHONE', '012 345 678 / 098 765 432')
SHOP_ADDRESS = os.getenv('SHOP_ADDRESS', 'Phnom Penh, Cambodia')
SHOP_ADDRESS_KH = os.getenv('SHOP_ADDRESS_KH', 'រាជធានីភ្នំពេញ, ប្រទេសកម្ពុជា')

# Currency Settings
EXCHANGE_RATE_USD_TO_KHR = Decimal(os.getenv('EXCHANGE_RATE_USD_TO_KHR', '4100'))
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'USD')

# Telegram Bot (@VeasnaKafebot)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '9157369786:AAFgBON0R6eAd9HzuYseuMlByyLY4H1yxgU')
TELEGRAM_OWNER_CHAT_ID = os.getenv('TELEGRAM_OWNER_CHAT_ID', '8414489462')
