from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def enviar_notificacion_a_alumno(canal, mensaje):
    print(f"Enviando notificación a {canal}: {mensaje}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"grupo_{canal}",  # El grupo específico del alumno basado en su identificador (ej. CURP)
        {
            "type": "notificacion_message",  # Este es el tipo de evento que se manejará en el consumer
            "text": mensaje,
        }
    )
