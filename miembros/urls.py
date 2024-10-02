from django.urls import path
from .views import RegistroMiembro,DatosMiembro,FotoCredencial 

urlpatterns = [
    path('registrar/', RegistroMiembro.as_view(), name='registrar_miembro'),
    path('credencial/', DatosMiembro.as_view(), name='credencial_miembro'),
    path('foto_credencial/', FotoCredencial.as_view(), name='foto_credencial'), 
]