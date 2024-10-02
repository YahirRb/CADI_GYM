from django.urls import path
from .views import Clases,RegistrarAsistencia

urlpatterns = [
    path('clases/', Clases.as_view(), name='clases'),
    path('asistencia/', RegistrarAsistencia.as_view(), name='asistencia'),
]