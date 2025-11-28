import boto3
import os
import sys
from botocore.client import Config

def load_env_file(filepath):
    """Carga variables de entorno desde un archivo .env si python-dotenv no está disponible."""
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                value = value.strip("'\"")
                env_vars[key.strip()] = value
    return env_vars

def delete_bucket_recursive(bucket_name):
    # Cargar credenciales
    env_vars = load_env_file('.env.local')

    # Obtener configuración
    endpoint = env_vars.get('AWS_S3_ENDPOINT_URL') or os.environ.get('AWS_S3_ENDPOINT_URL') or "https://s3.pek-pet.com"
    access_key = env_vars.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = env_vars.get('AWS_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = env_vars.get('AWS_S3_REGION_NAME') or os.environ.get('AWS_S3_REGION_NAME') or 'us-east-1'

    if not access_key or not secret_key:
        print("Error: No se encontraron las credenciales.")
        return

    s3 = boto3.resource('s3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name=region
    )
    
    bucket = s3.Bucket(bucket_name)

    try:
        # Verificar si existe
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"No se pudo encontrar el bucket '{bucket_name}'. Error: {e}")
        return

    # Contar objetos
    objects = list(bucket.objects.all())
    count = len(objects)

    if count > 0:
        print(f"El bucket '{bucket_name}' contiene {count} objetos.")
        confirm = input("¿Estás seguro de que quieres ELIMINAR TODOS LOS OBJETOS y el bucket? (escribe 'si' para confirmar): ")
        if confirm.lower() != 'si':
            print("Operación cancelada.")
            return
        
        print("Eliminando objetos...")
        bucket.objects.all().delete()
        print("Objetos eliminados.")
    else:
        print(f"El bucket '{bucket_name}' está vacío.")

    print(f"Eliminando bucket '{bucket_name}'...")
    try:
        bucket.delete()
        print("¡Bucket eliminado exitosamente!")
    except Exception as e:
        print(f"Error al eliminar el bucket: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bucket_name = sys.argv[1]
    else:
        bucket_name = input("Introduce el nombre del bucket a ELIMINAR: ").strip()
    
    if bucket_name:
        delete_bucket_recursive(bucket_name)
    else:
        print("Se requiere un nombre de bucket.")
