from __future__ import unicode_literals
from django.db import models
from uuid import uuid4
from .managers import UserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone


ROLES = (
    ('cliente', 'Cliente'),
    ('veterinario', 'Veterinario'),
    ('sucursal', 'Sucursal')
)


class User(AbstractUser):

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Cambia 'custom_user_set' por el nombre que prefieras
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Cambia 'custom_user_permissions' por el nombre que prefieras
        blank=True
    )

    phone = models.CharField(max_length=10, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='cliente')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email
    

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    @classmethod
    def generate_code(cls, user):
        # Eliminar códigos antiguos
        cls.objects.filter(user=user, created_at__lt=timezone.now() - timedelta(minutes=5)).delete()
        
        # Generar nuevo código
        code = secrets.randbelow(1000000)
        code_str = str(code).zfill(6)

        return cls.objects.create(user=user, code=code_str)
    
    def mark_as_used(self):
        """Marca el código como utilizado"""
        self.is_used = True
        self.save()

    def is_valid(self):
        return (not self.is_used) and (timezone.now() <= self.created_at + timedelta(minutes=5))
