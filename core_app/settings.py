from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-fl8s2_@1dea=y_&l)pivo=hi!8w8jq-4&s_rjcv&&x$b0hi&s#", 
)

DEBUG = bool(os.getenv("DEBUG", default=0))

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", default="http://127.0.0.1:8000").split(',')
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="*").split(',')
CSRF_COOKIE_DOMAIN = os.getenv("CSRF_COOKIE_DOMAIN", default="")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", default='http://127.0.0.1:8000').split(',')

CORS_ALLOW_HEADERS = [
    '*',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'django_extensions',
    'rest_framework_simplejwt',
    'storages',
    'django_filters',
]

INSTALLED_APPS = [
    *DJANGO_APPS,
    *THIRD_PARTY_APPS,
    'common',
    'users',
    'user_auth',
    'uploads',
    'hls',
    'titles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if not DEBUG:
    MIDDLEWARE.append('django.middleware.csrf.CsrfViewMiddleware')
    
ROOT_URLCONF = 'core_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', default='postgres_name'),
        'USER': os.getenv('POSTGRES_USER', default='postgres_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres_password'),
        'HOST': os.getenv('POSTGRES_HOST', default='localhost'),
        'PORT': os.getenv('POSTGRES_PORT', default='5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}
#DATABASES['default']['HOST'] = 'localhost'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if DEBUG else "ERROR",
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "INFO" if DEBUG else "ERROR",
            "propagate": False,
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'TITLE',
    'DESCRIPTION': 'DESCRIPTION',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '10000/day',
    },
}

CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', "redis://redis:6379/0") 
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://redis:6379/0") 
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_IGNORE_RESULT = False
CELERY_TASK_RETRY_COUNTDOWN = 30
CELERY_EAGER_PROPAGATES = DEBUG
CELERY_RESULT_EXPIRES = 60 * 60

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60) if not DEBUG else timedelta(minutes=600),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

MEDIA_ROOT = None

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STORAGES = {
    "default": {
        "BACKEND": "common.storages.UploadedFilesStorage",
        "OPTIONS":{
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
            "endpoint_url":"http://minio:9000",
            'bucket_name':'media',
            'use_ssl': not DEBUG,
        },
    },
    "staticfiles": {
        "BACKEND": "common.storages.StaticFilesStorage",
        "OPTIONS":{
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
            "endpoint_url":"http://minio:9000",
            'bucket_name':'static',
            'use_ssl': not DEBUG,
        },
    },
}