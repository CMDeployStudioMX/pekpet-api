from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from .models import User


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def client(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(ClientSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)
    