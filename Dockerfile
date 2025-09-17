# Usa una imagen base más específica
FROM python:3.10-slim-bullseye

# Establece variables de entorno para evitar prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo
WORKDIR /code

# Instala dependencias del sistema primero (como root)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea usuario y cambia permisos
RUN useradd -m -u 1000 user && \
    chown -R user:user /code

USER user

# Actualiza pip e instala dependencias de Python
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copia el proyecto
COPY --chown=user:user . /code/

# Expone el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD sh -c "python manage.py collectstatic --noinput && python manage.py migrate && /home/user/.local/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"