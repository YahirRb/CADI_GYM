from django.urls import path
from .views import PagosPendientesUsuario,RegistrarPago

urlpatterns = [
    path('pendiente_usuario/', PagosPendientesUsuario.as_view(), name='pagos_pendientes_usuarios'),
    path('realizar_pago/', RegistrarPago.as_view(), name='registrar_pago'),
]