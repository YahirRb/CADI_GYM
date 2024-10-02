from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import GimnasioMixto, GimnasiaArtistica

@receiver(post_migrate)
def create_default_modalities(sender, **kwargs):
    # Asegúrate de que solo se ejecute para tu aplicación específica
    if sender.name == 'inscripciones':
        # Datos predeterminados para GimnasioMixto
        default_gimnasio_mixto = [
            {"modalidad": "Visita", "costo": 70.00},
            {"modalidad": "Semana", "costo": 200.00},
            {"modalidad": "Quincena", "costo": 300.00},
            {"modalidad": "Mes", "costo": 550.00},
            {"modalidad": "Trimestre", "costo": 1250.00},
            {"modalidad": "6 Meses", "costo": 2500.00},
        ]
        
        for value in default_gimnasio_mixto:
            GimnasioMixto.objects.get_or_create(modalidad=value["modalidad"], costo=value["costo"])

        # Datos predeterminados para GimnasiaArtistica
        default_gimnasia_artistica = [
            {"modalidad": "Visita", "costo": 80.00},
            {"modalidad": "Mes (de 5 a 6 años)", "costo": 730.00},
            {"modalidad": "Mes (7 años en adelante)", "costo": 810.00}
        ]
        
        for value in default_gimnasia_artistica:
            GimnasiaArtistica.objects.get_or_create(modalidad=value["modalidad"], costo=value["costo"])
