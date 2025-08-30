from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import *
from .models import User


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    # @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    # def change_password(self, request):
    #     data = request.data
    #     user = request.user

    # @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny])
    # def get_code(self, request):

    # @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    # def verify_code(self, request):
    #     # Generar token
    #     token = AccessToken()
    #     token.set_exp(lifetime=timedelta(minutes=10))  # Expiración personalizada