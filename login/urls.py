from django.urls import path
from .views import LogIn

urlpatterns = [
    path('login/', LogIn.as_view(), name='login'),
]