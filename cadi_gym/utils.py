 
from supabase import create_client
import os
import environ
from asgiref.sync import sync_to_async
from django.core.mail import send_mail, EmailMessage
from .settings import EMAIL_HOST_USER 
env = environ.Env()
 
environ.Env.read_env()

url = env('SUPABASE_URL')
key = env('SUPABASE_KEY')
supabase= create_client(url, key)
#@sync_to_async
def enviar_correo(destinatario, asunto, mensaje):
    remitente = EMAIL_HOST_USER  
    send_mail(
        asunto,
        mensaje,
        remitente,
        [destinatario],
        fail_silently=False,
    )