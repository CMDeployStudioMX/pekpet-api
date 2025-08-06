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

* Para ejecutar el proyecto, es necesario cumplir con los requerimientos técnicos.

### Pasos previos

#### Pyenv

Crear un entorno virtual con "pyenv" para aislar las librerías que usaremos con el proyecto y no perjudicar otros proyectos. Esta practica se realiza porque en algunos casos tenemos proyectos que usan las mismas librerías pero con versiones  distinas, esto puede cauzar algún  cruce de información  que podría perjudicar el funcionamiento de varios proyectos.
