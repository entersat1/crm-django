"""
Django settings for core project.
"""

import os
from pathlib import Path

# --- Rutas y Configuración de Seguridad ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-bomba-atomica-2098869856'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
INTERNAL_IPS = ['127.0.0.1']


# --- Definición de Aplicaciones ---
INSTALLED_APPS = [
    'baton',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps de Terceros
    'import_export',
    'debug_toolbar',
    
    # Mis Apps
    'clientes',
    'inventario',
    'servicios',
    
    
    
    

    'baton.autodiscover',
]

# --- Middleware ---
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLs, Plantillas y Servidor ---
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
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
                'configuracion.context_processors.configuracion_global',
            ],
        },
    },
]

# --- Base de Datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {'timeout': 20}
    }
}

# --- Validación de Contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internacionalización ---
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# --- Archivos Estáticos y Media ---
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Otros Ajustes ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/admin/login/'

# --- Configuración de Email ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.zonalitoral.com.ar'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ventas@zonalitoral.com.ar'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'la_contraseña_de_tu_email')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- Configuración de Caché ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# --- Configuración de Baton ---
BATON = {
    'SITE_HEADER': 'Administración del Taller',
    'SITE_TITLE': 'Mi Taller',
    'INDEX_TITLE': 'Panel de Control',
    'SUPPORT_HREF': 'mailto:soporte@tuemail.com',
    'COPYRIGHT': 'copyright © 2025 Mi Taller',
    'POWERED_BY': '<a href="#">Tu Empresa</a>',
}