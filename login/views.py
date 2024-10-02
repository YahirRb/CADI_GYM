from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken 

User = get_user_model()

class LogIn(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = User.objects.get(username=username)

            if not user.check_password(password):
                return Response(data={"detail": "Usuario o contraseña incorrectos"}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response(data={"detail": "Necesita verificación"}, status=status.HTTP_401_UNAUTHORIZED)

            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                # Obtener el token de acceso del cuerpo de la respuesta
                token = response.data.get('access')
                # Decodificar el token para acceder a su payload
                decoded_token = AccessToken(token)
                # Agregar el campo isAdmin al payload
                decoded_token['user_id']=user.username
                decoded_token['isAdmin'] = user.is_superuser
                decoded_token['rol']=user.roles
                decoded_token['tema']=user.tema
                # Actualizar el token en la respuesta con los nuevos datos del payload
                response.data['access'] = str(decoded_token)
                

                return response

        except User.DoesNotExist:
            return Response(data={"detail": "Usuario o contraseña incorrectos"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(data={"detail": "Ocurrio un error"}, status=status.HTTP_400_BAD_REQUEST)