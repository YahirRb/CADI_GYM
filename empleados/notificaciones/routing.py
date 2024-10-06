from django.urls import re_path
from empleados.notificaciones import consumers 
websocket_urlpatterns=[
    
    re_path(r'ws/notificaciones/(?P<canal>\w+)/$', consumers.NotificationConsumer.as_asgi()),
    #re_path(r'ws/notificaciones/', consumers.NotificationConsumer.as_asgi()),
]