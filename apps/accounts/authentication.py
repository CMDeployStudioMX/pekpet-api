from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

class TemporaryTokenAuthentication(JWTAuthentication):
    """
    Authentication personalizada para tokens temporales
    """
    
    def authenticate(self, request):
        try:
            # Usar la autenticación base de JWT
            auth_result = super().authenticate(request)
            
            if auth_result is None:
                return None
                
            user, token = auth_result
            
            # Puedes agregar validaciones adicionales aquí si necesitas
            # Por ejemplo, verificar que el token sea específico para cambio de password
            
            return (user, token)
            
        except TokenError as e:
            raise AuthenticationFailed({'error': 'Token inválido o expirado'})
        except Exception as e:
            raise AuthenticationFailed({'error': 'Error de autenticación'})
