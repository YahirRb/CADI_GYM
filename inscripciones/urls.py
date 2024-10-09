from django.urls import path
from .views import Clases,RegistrarAsistencia,CambioModalidad,RegistrarInscripcion,NotificarPagos,InscripcionesMiembro,BajaInscripcion,AsistenciaDiaActual

urlpatterns = [
    path('clases/', Clases.as_view(), name='clases'),
    path('asistencia/', RegistrarAsistencia.as_view(), name='asistencia'),
    path('cambio_modalidad/', CambioModalidad.as_view(), name='cambio_modalidad'),
    path('nueva_inscripcion/', RegistrarInscripcion.as_view(), name='nueva_inscripcion'),
    path('notificaciones/', NotificarPagos.as_view(), name='notificaciones'),
    path('baja/', BajaInscripcion.as_view(), name='baja_inscripcion'),
    path('inscripciones/', InscripcionesMiembro.as_view(), name='inscripciones_usuario'),
    path('asistencias_dia/', AsistenciaDiaActual.as_view(), name='asistencias_dia'),
]