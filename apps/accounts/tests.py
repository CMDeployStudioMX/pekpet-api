from django.test import TestCase
from .models import *

# Create your tests here.
class UserTest(TestCase):

    # Inizialización de los datos que usaremos para las pruebas
    def setUp(self):
        temporal_user = User.objects.create(
            username='testuser',
            first_name='Test',
            last_name='Temporal',
            email='temporal@mail.com'
        )
        temporal_user.set_password('Test12345.')
        temporal_user.save()

    def get_user(self):
        "get user"

        temporal_user = User.objects.get(email='temporal@mail.com')
        print(temporal_user.name)
