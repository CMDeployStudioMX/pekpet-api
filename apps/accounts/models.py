from __future__ import unicode_literals
from django.db import models
from uuid import uuid4
from .managers import UserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email
