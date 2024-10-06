from django.urls import path
from .views import LogIn,RefreshTokenView

urlpatterns = [
    path('login/', LogIn.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
]