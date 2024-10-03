from django.db.models.signals import post_migrate
from django.dispatch import receiver
from miembros.models import Miembro, HistorialMedico, HistorialDeportivo

@receiver(post_migrate)
def create_default_members(sender, **kwargs):
    # Asegúrate de que solo se ejecute para tu aplicación específica
    if sender.name == 'tu_nombre_de_aplicacion':  # Cambia esto por el nombre de tu aplicación
        # Datos predeterminados para Miembro
        default_members = [
            {
                "fecha": "2024-01-01",
                "nombre": "Juan",
                "apellidos": "Pérez",
                "direccion": "Calle Falsa 123",
                "fecha_nacimiento": "1990-01-01",
                "edad": 34,
                "tipo_sangre": "O+",
                "facebook": "https://facebook.com/juanperez",
                "correo": "juan.perez@example.com",
                "curp": "PEPJ901001HDFRNS00",
                "nss": "12345678901",
                "dependencia": "Ninguna",
                "telefono_fijo": "5551234567",
                "celular": "5559876543",
                "hijos": 2,
                "edades": "[5, 7]",
                "padre_tutor": "Pedro Pérez",
                "telefono_tutor": "5557654321",
                "contacto_emergencia": {"nombre": "Luis", "telefono": "5551112233"},
                "foto": None  # Agrega la ruta a la foto si es necesario
            },
            # Agrega más miembros según sea necesario
        ]

        for member_data in default_members:
            miembro, created = Miembro.objects.get_or_create(
                correo=member_data["correo"],
                defaults=member_data
            )
            
            # Crear HistorialMedico si el miembro fue creado
            if created:
                HistorialMedico.objects.get_or_create(
                    miembro=miembro,
                    defaults={
                        "padecimientos": None,
                        "medicamentos": None,
                        "descripcion_accidente": None,
                        "descripcion_operacion": None,
                        "descripcion_hospitalizacion": None,
                        "desmayos_ejercicio": None,
                        "traumatismo_oseo": None,
                        "golpe_cabeza": None,
                        "alergias": None,
                        "enfermedad_actual": None,
                        "observaciones": None,
                    }
                )

                # Crear HistorialDeportivo si el miembro fue creado
                HistorialDeportivo.objects.get_or_create(
                    miembro=miembro,
                    defaults={
                        "deporte_actual": None,
                        "actividad_fisica_reciente": None,
                        "lesion": None,
                    }
                )
