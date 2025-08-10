from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import *
from .models import User


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    def client_register(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': ClientSerializer(user).data,
                'message': 'User created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
