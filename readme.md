# API V2 Template

## Contenido

- Template de la API V2 desarrollada en Python3 en el framework Django con otras librerías.

### Librerías

- DJANGO 5.0.X
- DJANGO REST FRAMEWORK 3.15.X
- PSYCOPG 3.1.X
- JWT 2.8.X
- Celery 5.4.x

---

## Requerimientos técnicos

- Python 3.10.X
- Pyenv
- PostgreSQL
- Docker
- RabbitMQ
- Min.IO

### Sugerencias

Para el buen funcionamiento del proyecto y sus librerías, es recomendable tener un equipo con un sistema basado en UNIX:

- MacOS
- Distribuciones Linux/Debian (Recomendado Ubuntu)
- WSL (Windows Subsystem for Linux)

---

## Instalación del proyecto

- Para ejecutar el proyecto, es necesario cumplir con los requerimientos técnicos mencionados anteriormente.

### Pasos previos

#### Pyenv

Crear un entorno virtual con "pyenv" para aislar las librerías que usaremos con el proyecto y no perjudicar otros proyectos. Esta practica se realiza porque en algunos casos tenemos proyectos que usan las mismas librerías pero con versiones  distinas, esto puede cauzar algún  cruce de información  que podría perjudicar el funcionamiento de varios proyectos.

Para ello, usaremos el proyecto [Pyenv](https://github.com/pyenv/pyenv).

- Para instalarlo, dependiendo del sistema, nos apoyamos de la siguiente [documentación](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)

  - Si presentamos algun error al instalar pyenv, es necesario instalar las [dependencias](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)

- Luego instalamos la versión de Python que necesitamos para el proyecto con:

```bash
pyenv install 3.10
```

- Luego creamos nuestro entorno virtual con:

```bash
pyenv virtualenv 3.10 "nombre del entorno"
```

- Y para activarlo, usamos:

```bash
pyenv activate "nombre del entorno"
```

### Instalar dependencias

Para instalar las dependencias es necesario posicionarnos en la carpeta del proyecto, de tal forma que tengamos acceso al archivo "requirements.txt", previamente tenemos que tener activado el entorno virtual y seguido debemos de ejecutar el siguiente comando:

```python
pip install -r requirements.txt
```

### Base de datos

Para la base de datos es necesario que tengamos PostgreSQL en su versión 16 en adelante, creamos un usuario y contraseña que más adelante lo usaremos para conectarnos, también es necesario crear una base de datos para el proyecto, nos apoyamos de la siguiente documentación:

[Instalar PostgreSQL](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04-es?utm_medium=affiliates&utm_source=impact&utm_campaign=123201&utm_content=231384&irgwc=1&irclickid=xipS17ye4xycTSQUq6T0OTFaUkp2Mn3QNWFFx80)

[Crear usuario para PostgreSQL](https://medium.com/crehana/creaci%C3%B3n-de-usuario-en-postgresql-10-4-y-ubuntu-18-04-9e80fe077f7e)

Es necesario que tengamos a la mano la siguiente información:

- Usario
- Contraseña
- Nombre de la base de datos
- Puerto (En caso de haber modificado el puerto por defecto de PostgreSQL)

---

## Variables de entorno

Para correr el proyecto necesitamos contar con las siguientes variables de entorno:

```json
# Variables de entorno para el funcionamiento de la API

# DEBUG nos servirá para ver los logs del sistema
export DEBUG=1

# Es una palabra secreta alfanumérica que nos sirve para varios procesos, como hashear información
export SECRET_KEY=P3kp3t0k3nS3cr3tK3y 

# Conexión a la base de datos

# Información que obtuvimos en el paso anterior
export DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/nombre_bd"

# Dominios pueden hacer peticiones a la API
export ALLOWED_HOST="localhost 127.0.0.1"

# CRSF Origins
# URLs (http o https) que tienen autorización para hacer peticiones
export CSRF_ORIGINS="http://localhost http://127.0.0.1"
```

Esta información la debemos de tener en un archivo .env para poder cargar estas variables en nuestra sesión en consola que tengamos abierta en nuestro IDE de preferencia.

Cada nueva sesión que habramos de la terminal es necesario activar nuestro entorno pyenv y cargar nuevamente variables de entorno

Para que nuestras variables sean visibles para el proyecto nos apoyamos del siguiente comando:

El archivo tiene que comenzar con ".env" seguido de otro punto y luego el nombre que nosotros queramos, se sugiere usar el nombre que aparece en el comando.

```bash
source .env.local
```

### Cargar tablas a nuestra base de datos

Si lo anterior salió bien, ahora podremos cargar nuestra estructura de la base de datos a la que creamos anteriormente, para ello nos apoyamos del siguiente comando:

```python
python manage.py migrate
```

Migrará todos los cambios a nuestra base de datos para tener la ultima estructura de nuestra información para trabajar localmente.

Seguido de esto, es necesario que creemos un superusuario local para acceder al django admin y otros apartados, para ello usamos este comando

```python
python manage.py createsuperuser
```

Nos pedirá un usuario, correo electrónico y contraseña, te recomiendo usar el correo electrónico para el usuario.

---

## Levantar el proyecto

Una vez finalizado con los pasos anteriores, podremos levantar el proyecto con el siguiente comando:

```python
python manage.py runserver
```

Y con esto podremos acceder al Django admin o a los otros apartados.