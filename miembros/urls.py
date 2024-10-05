from django.urls import path
from .views import RegistroMiembro,DatosMiembro,FotoCredencial,RegistroVisitante,ListarVisitantes,SuspenderMiembro, RegistroTemporal,MiembrosActivos,EnlaceTemporal,VisitantesRegistrados

urlpatterns = [
    path('registrar/', RegistroMiembro.as_view(), name='registrar_miembro'),
    path('credencial/', DatosMiembro.as_view(), name='credencial_miembro'),
    path('foto_credencial/', FotoCredencial.as_view(), name='foto_credencial'), 
    path('registrar_visitante/', RegistroVisitante.as_view(), name='registrar_visitante'), 
    path('listar_visitantes/', ListarVisitantes.as_view(), name='listar_visitantes'),
    path('suspender_miembro/', SuspenderMiembro.as_view(), name='suspender_miembro'),
    path('registro_temporal/', RegistroTemporal.as_view(), name='registro_temporal'),
    path('activos/',MiembrosActivos.as_view(), name='activos'),
    path('enlace/',EnlaceTemporal.as_view(), name='enlace'),
    path('visitante_existente/', VisitantesRegistrados.as_view(), name='visitante_existente'),
]
