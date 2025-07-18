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

ALLOWED_HOSTS = [
    'ischool-backend.onrender.com',
    "ischool.ng",
    "www.ischool.ng",
    "api.ischool.ng",
]

CORS_ALLOW_METHODS = list(default_methods) + [
    'POST',
]

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
    "corsheaders.middleware.CorsMiddleware",  # ✅ MUST BE FIRST
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
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": SECRET_KEY,
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

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://www.ischool.ng",  # Your production frontend
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = False


CSRF_TRUSTED_ORIGINS = [
    "https://www.ischool.ng",
    "https://api.ischool.ng",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',
    'X-CSRFToken',
    'Content-Type',
]

# Logging
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
    #OLE PLAN
    "ole_monthly": "PLN_8zqxfh5dmamqena",

    #OLA PLANS
    "ola_monthly": "PLN_ggznevdmbw5pjb4",
    "ola_yearly": "PLN_r1rhq04xs8yd3uv"
}


PAYSTACK_PLAN_AMOUNTS = {
    #Ole plan amounts
    "ole_monthly": 10000,

    #Ola plans amounts
    "ola_monthly": 610000,
    "ola_yearly": 5200000,
}

# Celery
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'run-weekly-summary-every-monday': {
        'task': 'apps.tasks.weekly_summary.generate_weekly_summary',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),
    },
}

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#SLOT_PRICE_MONTHLY = 6100, SLOT_PRICE_YEARLY = 52000

# Other constants
SLOT_PRICE_MONTHLY = 6100
SLOT_PRICE_YEARLY = 52000


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
