from django.urls import path
from .views import RegistroMiembro

urlpatterns = [
    path('registrar/', RegistroMiembro.as_view(), name='registrar_miembro'),
]