"""
Django settings for config project.

Base generada originalmente con Django 5.2.18 y conservada para Django 6.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^qy@i#x-(ze+r*g7f0fac$&7ij(!2$lso(^tiz#rvqgcmou=ya'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'main.operario',
    'main.clienteFinal',
    'main.repartidor',
    'main.homePage',
    'main.users'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL and DATABASE_URL.startswith(('postgres://', 'postgresql://')):
    # Habilitar pool de conexiones entre hilos para desarrollo en Windows
    from config.pool import enable_connection_pooling
    enable_connection_pooling()

    # Con pool activado, Django requiere conn_max_age=0 para que al finalizar
    # cada request la conexión vuelva inmediatamente al pool y quede disponible
    # para el próximo request en cualquier hilo, evitando reconexiones SSL.
    db_config = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=0,
        conn_health_checks=True,
    )
    options = db_config.setdefault('OPTIONS', {})
    options.update({
        # Acota la espera del intento TCP a 5 s por IP
        'connect_timeout': 5,
        # TCP keepalives: detectan sockets half-open sin esperar el timeout del
        # SO de Windows (~2 h).
        'keepalives': 1,
        'keepalives_idle': 30,      # iniciar sondeos tras 30 s de inactividad
        'keepalives_interval': 10,  # re-sondear cada 10 s
        'keepalives_count': 3,      # 3 sondeos fallidos = socket muerto
        'pool': {'min_size': 1, 'max_size': 5, 'timeout': 10.0},
    })

    # En Windows, getaddrinfo para el host de Neon devuelve primero direcciones IPv6
    # (AWS). Si el ISP/red no tiene ruteo IPv6 funcional, cada nueva conexión TCP
    # (incluidos los workers/hilos de runserver) espera 3 x 5s = 15 s de timeout
    # antes de probar IPv4. Al resolver la IP IPv4 y pasarla como 'hostaddr',
    # libpq conecta directamente por IPv4 en ~1s, manteniendo 'host' para SNI y TLS.
    host = db_config.get('HOST')
    if host:
        try:
            import socket
            ipv4_candidates = [
                addr[4][0] for addr in socket.getaddrinfo(host, 5432, socket.AF_INET)
            ]
            if ipv4_candidates:
                options['hostaddr'] = ipv4_candidates[0]
        except Exception:
            pass

    DATABASES = {
        'default': db_config,
    }
else:
    # Desarrollo local con SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cache y sesiones en memoria local con respaldo en DB (cached_db):
# Evita un round-trip SQL a la base remota en cada request para leer la sesión.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sgr-cache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

AUTHENTICATION_BACKENDS = [
    'main.users.backends.CachedModelBackend',
]
# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'

# Carpetas extra donde buscar estáticos (además de las de cada app)
STATICFILES_DIRS = [BASE_DIR / 'static']

# Carpeta destino de collectstatic (solo producción)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/6.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy
CRISPY_TEMPLATE_PACK = "bootstrap5"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

###

LOGIN_URL = 'login'

AUTH_USER_MODEL = 'users.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'