import os
import dj_database_url

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg3",
        "NAME": "postgres"
    }
}

# Obtener URI de la base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASES["default"] = dj_database_url.config(
    default=DATABASE_URL,
    conn_max_age=0
)
