from django.urls import path
from .views import Clases

urlpatterns = [
    path('clases/', Clases.as_view(), name='clases'),
]