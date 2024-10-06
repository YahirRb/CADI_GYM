from django.urls import path 
from .views import RegistroEmpleado,ListarEmpleados,EstadoEmpleado

urlpatterns = [
    path('registro/', RegistroEmpleado.as_view(), name='registro_empleado'), 
    path('lista_empleados/', ListarEmpleados.as_view(), name='lista_empleado'), 
    path('estado/', EstadoEmpleado.as_view(), name='estado_empleado'), 
]