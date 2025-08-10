from django.contrib.auth.models import Group
from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
