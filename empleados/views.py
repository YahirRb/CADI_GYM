from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND
from .models import Empleados
from .serializers import EmpleadoSerializer
from datetime import datetime, timedelta
from django.utils import timezone 
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
# Create your views here.

class RegistroEmpleado(APIView):
    def post(self,request):
        try:
            password=request.data.get('password')
            nombre_completo=request.data.get('nombre_completo')
            correo=request.data.get('correo')
            telefono=request.data.get('telefono')
            datos_empleado={
                'nombre_completo':nombre_completo,
                'correo':correo,
                'telefono':telefono
            }
            
            serializer= EmpleadoSerializer(data=datos_empleado)
            if serializer.is_valid():
                serializer.save()
                User = get_user_model()
                rol, created = Group.objects.get_or_create(name='employee')
                user, created = User.objects.get_or_create(
                    username=correo,
                    defaults={
                        'email': correo,
                        'first_name':nombre_completo,
                        'password':  password,
                        'roles':rol.name
                    }
                )
                user.groups.add(rol)
                return Response(data="Empleado registrado",status=HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(data="Hay un error en los datos",status=HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)


class ListarEmpleados(APIView):
    def get(self,request):
        try:
            empleados=Empleados.objects.filter(activo=True) 
            serializer=EmpleadoSerializer(empleados,many=True)
            return Response(data=serializer.data,status=HTTP_200_OK)
            
        except Exception as e:
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)


class EstadoEmpleado(APIView):
    def put(self,request):
        try:
            User=get_user_model()
            id_empleado = request.data.get('id_empleado')
            estado=request.data.get('estado')
            empleado= Empleados.objects.get(id=id_empleado)
            user=User.objects.get(email=empleado.correo)
            empleado.activo=estado
            user.is_active=estado
            empleado.save()
            user.save()
            
            return Response(data="Estado actualizado",status=HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)        


