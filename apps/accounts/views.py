from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging
from .emails import send_email
from .serializers import UserSerializer
from .authentication import TemporaryTokenAuthentication
from .models import VerificationCode  # ← Importar el modelo

logger = logging.getLogger(__name__)
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['get_code', 'verify_code']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['POST'], authentication_classes=[TemporaryTokenAuthentication])
    def change_password(self, request):
        """
        Endpoint para cambiar contraseña - Requiere token temporal
        """
        user = request.user
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response(
                {'error': 'current_password y new_password son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña cambiada exitosamente'})

    @action(detail=False, methods=['GET'])
    def get_code(self, request):
        """
        Endpoint público para solicitar código de verificación
        """
        email = request.GET.get('email')
        
        if not email:
            return Response(
                {'error': 'El parámetro email es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email, is_active=True, is_staff=False, is_superuser=False)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            if VerificationCode.objects.filter(user=user, is_used=False, created_at__gte=timezone.now() - timedelta(minutes=5)).exists():
                return Response(
                    {'error': 'Ya se ha enviado un código recientemente. Revisa tu email.'}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Generar código de verificación usando el modelo
            verification_code = VerificationCode.generate_code(user)
            
            # En producción: enviar por email/SMS (aquí solo logueamos)
            logger.info(f"Código de verificación para {email}: {verification_code.code}")

            # Logica para enviar email
            send_email(verification_code.code, to_email=email)
            
            return Response({
                'message': 'Código enviado exitosamente', 
                'user_id': user.id,
                'code': verification_code.code  # ← No enviar en producción!
            })

            # return Response({
            #     'message': 'Código enviado exitosamente', 
            #     'user_id': user.id
            # })
            
        except Exception as e:
            logger.error(f"Error generando código para {email}: {str(e)}")
            return Response(
                {'error': 'Error al generar el código'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['POST'])
    def verify_code(self, request):
        """
        Endpoint público para verificar código y obtener token temporal
        """
        user_id = request.data.get('user_id')
        code = request.data.get('code')
        
        if not user_id or not code:
            return Response(
                {'error': 'user_id y code son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            
            # Buscar el código más reciente para este usuario
            verification_code = VerificationCode.objects.filter(
                user=user, 
                code=code
            ).order_by('-created_at').first()
            
            if not verification_code:
                return Response(
                    {'error': 'Código inválido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si el código es válido
            if not verification_code.is_valid():
                return Response(
                    {'error': 'Código expirado o ya utilizado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Marcar código como usado
            verification_code.mark_as_used()
            
            # Generar token JWT temporal
            token = AccessToken.for_user(user)
            token.set_exp(lifetime=timedelta(minutes=10))
            
            return Response({
                'token': str(token),
                'expires_in': 600,
                'message': 'Código verificado exitosamente. Usa este token para cambiar la contraseña.'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error en verify_code: {str(e)}")
            return Response(
                {'error': 'Error en la verificación'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
