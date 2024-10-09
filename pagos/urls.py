from django.urls import path
from .views import PagosPendientesUsuario,RegistrarPago,PagosPendientes,PagosFiltro

urlpatterns = [
    path('pendiente_usuario/', PagosPendientesUsuario.as_view(), name='pagos_pendientes_usuarios'),
    path('realizar_pago/', RegistrarPago.as_view(), name='registrar_pago'),
    path('pendientes/', PagosPendientes.as_view(), name='pagos_pendientes'),
    path('filtro_pago/', PagosFiltro.as_view(), name='filtro_pago'),
]