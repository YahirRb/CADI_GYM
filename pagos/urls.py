from django.urls import path
from .views import PagosPendientesUsuario

urlpatterns = [
    path('pendiente_usuario/', PagosPendientesUsuario.as_view(), name='pagos_pendientes_usuarios'),
]