# Librerías de django

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Librerías de terceros

THIRD_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'corsheaders'
]

# Apps o módulos del proyecto

LOCAL_APPS = [
    'accounts',
    'logs'
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_APPS
