from pathlib import Path
from datetime import timedelta
import os
from decouple import config
from dotenv import load_dotenv
from celery.schedules import crontab
import logging
import dj_database_url
from corsheaders.defaults import default_headers
from corsheaders.defaults import default_methods

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS — always prefer the explicit env var, in every environment.
# Falling back to ['*'] only when DEBUG is on AND nothing is configured means a
# single stray DEBUG=True in production can't silently open the host to the world
# unless ALLOWED_HOSTS is also empty.
_hosts = config('ALLOWED_HOSTS', default='')
if _hosts:
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
    "users",
    "school",
    "corsheaders",
    "rest_framework_simplejwt",
    "teacher_dashboard",
    "student_dashboard",
    "parent_dashboard",
    "test_app",
    "payments",
    "teachers",
    "django_filters",
    "rest_framework.authtoken",
    "elibrary",
    'django_celery_beat',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "iSchool_Ola.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "iSchool_Ola.wsgi.application"

# Database
# ssl_require is now only enforced outside DEBUG, so local dev against a
# non-SSL Postgres (e.g. Homebrew/Docker) still works.
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Django 4.2+ replacement for the deprecated STATICFILES_STORAGE setting.
# Same Whitenoise backend, just declared through the modern STORAGES dict.
# Required on Django 5.1+ where STATICFILES_STORAGE was removed entirely.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_THROTTLE_RATES': {
        'otp': '5/min',
        'login': '10/min',
        'register': '20/hour',
    },
    'NUM_PROXIES': 1,
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": config("JWT_SIGNING_KEY", default=SECRET_KEY),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.MyTokenObtainPairSerializer",
}

AUTH_USER_MODEL = 'users.CustomUser'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.ischool.ng'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'noreply@ischool.ng'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'noreply@ischool.ng'
CONTACT_EMAIL = "admin@ischool.ng"
EMAIL_TIMEOUT = 10

# ============================================
# CORS SETTINGS - Production Ready
# ============================================

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOW_CREDENTIALS = True
    # Localhost entries removed from the production list; they still work in DEBUG.
    CORS_ALLOWED_ORIGINS = [
        "https://www.ischool.ng",
        "https://api.ischool.ng",
        # Add your mobile app's production URL if applicable
    ]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Access-Control-Allow-Origin',
]

CORS_PREFLIGHT_MAX_AGE = 600

# ============================================
# CSRF SETTINGS - Production Ready
# ============================================

if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        "http://localhost:19000",
    ]
else:
    CSRF_TRUSTED_ORIGINS = [
        "https://www.ischool.ng",
        "https://api.ischool.ng",
    ]

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax' if DEBUG else 'Strict'

# ============================================
# Deployment / proxy
# ============================================
# Render terminates TLS and forwards plain HTTP to Django. Without this,
# request.is_secure() is always False, cookies may not be marked secure,
# and any redirect-based flow can end up in a loop.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================
# Production security headers
# ============================================
# Only applied when DEBUG is off, so local dev is untouched.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF_COOKIE_SECURE is already handled above; setting it here for clarity.
    CSRF_COOKIE_SECURE = True

    # HSTS — starts the 1-year clock. Remove these three lines if you ever
    # need to serve any *.ischool.ng subdomain over plain HTTP.
    SECURE_HSTS_SECONDS = 31536000          # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

# ============================================
# Logging - Production Ready
# ============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Paystack
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_LIVE_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_LIVE_SECRET_KEY')
PAYSTACK_CALLBACK_URL = "https://api.ischool.ng/ole-student/verify-payment"
OLE_PAYMENT_CALLBACK_URL = os.getenv("OLE_PAYMENT_CALLBACK_URL", "https://www.ischool.ng/ole-subscription/verify")

PAYSTACK_PLAN_IDS = {
    "monthly": "PLN_te234irfrrc753l",
    "ola_monthly": "PLN_3mqbv2tbtch9d2a",
    "ola_yearly": "PLN_b5q8x983srq1ei9",
}
PAYSTACK_PLAN_AMOUNTS = {
    "monthly":     10000,   # ₦100
    "ola_monthly": 10000,   # ₦100
    "ola_yearly":  10000,   # ₦100
}
# Slot prices (in kobo)
SLOT_PRICE_MONTHLY = 10000   # ₦100
SLOT_PRICE_YEARLY  = 10000   # ₦100
# Celery
CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/0')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'run-weekly-summary-every-monday': {
        # ⚠️ Verify this import path matches where the task actually lives.
        # If the module can't be imported, Celery beat will silently fail every Monday.
        'task': 'apps.tasks.weekly_summary.generate_weekly_summary',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),
    },
}

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

PAYMENT_CALLBACK_URL = "https://api.ischool.ng/api/payments/payment-callback/"

# Africa's Talking SMS Configuration
AFRICASTALKING_USERNAME = config('AFRICASTALKING_USERNAME', default='sandbox')
AFRICASTALKING_API_KEY = config('AFRICASTALKING_API_KEY', default='')
AFRICASTALKING_SENDER_ID = config('AFRICASTALKING_SENDER_ID', default='iSchool')

# Silence Django's "no explicit primary key" model warning.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'