 
from supabase import create_client
import os
from asgiref.sync import sync_to_async
from django.core.mail import send_mail, EmailMessage
from .settings import EMAIL_HOST_USER 


url = 'https://zkhbfudrvxvtvnusmxsl.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpraGJmdWRydnh2dHZudXNteHNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNzczMzk5MCwiZXhwIjoyMDQzMzA5OTkwfQ.uJLTS4Am3EH2XpYrRZlmcqIy7b8Jtp0cdQy_TzD1bP8'
supabase= create_client(url, key)
@sync_to_async
def enviar_correo(destinatario, asunto, mensaje):
    remitente = EMAIL_HOST_USER  
    send_mail(
        asunto,
        mensaje,
        remitente,
        [destinatario],
        fail_silently=False,
    )