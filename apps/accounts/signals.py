from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import User

# Función para capturar una modificación o creación de un usario
@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if created:
        # Nuevo usuario
        print(instance.username)
    else:
        # Usuario modficado
        print(instance.username)


@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    print(instance.username)
