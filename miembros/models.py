from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.db import models

# Create your models here.
class Miembro(models.Model):
    
    num_control = models.AutoField(primary_key=True) 
    fecha = models.DateField()  # Fecha de registro automática # Número de control único
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    direccion = models.TextField()  # Almacenará direcciones largas
    fecha_nacimiento = models.DateField()
    edad = models.IntegerField()
    tipo_sangre = models.CharField(max_length=3) 
    facebook = models.TextField(blank=True, null=True)  # Opcional
    correo = models.EmailField(unique=True)  # Campo de correo único
    curp = models.CharField(max_length=18, unique=True)  # CURP única
    nss = models.CharField(max_length=11, unique=True)  # Número de seguridad social único
    dependencia = models.CharField(max_length=100)
    telefono_fijo = models.CharField(max_length=15, blank=True, null=True)
    celular = models.CharField(max_length=15)
    hijos = models.IntegerField(blank=True, null=True)  # Permitir nulos
    edades = models.CharField(max_length=100, blank=True, null=True)  # Permitir nulos
    padre_tutor = models.CharField(max_length=100, blank=True, null=True)  # Permitir nulos
    telefono_tutor = models.CharField(max_length=15, blank=True, null=True)
    contacto_emergencia = models.JSONField()  # Guardar como JSON
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.num_control}"
    
    def save(self, *args, **kwargs):
        
        # Llamar al método save del modelo
        super().save(*args, **kwargs)
        try:
            curp = self.curp  # Obtener CURP
            password_temporal = curp[:10]
            User = get_user_model()
            rol, created = Group.objects.get_or_create(name='miembro')
            user, created = User.objects.get_or_create(
                username=self.correo,
                defaults={
                    'email': self.correo,
                    'first_name':self.nombre,
                    'last_name':self.apellidos,
                    'password':  make_password(password_temporal),
                    'roles':rol.name
                }
            )
            user.groups.add(rol)
        except Exception as e:
            print(f"Error al crear el usuario: {e}")

    
class HistorialMedico(models.Model):
    miembro = models.OneToOneField(Miembro, on_delete=models.CASCADE, primary_key=True)
    padecimientos = models.JSONField(blank=True, null=True)  # Lista de padecimientos
    medicamentos = models.JSONField(blank=True, null=True)  # Lista de medicamentos, permitir nulos
    descripcion_accidente = models.TextField(blank=True, null=True)  # Descripción de accidente, permitir nulos
    descripcion_operacion = models.TextField(blank=True, null=True)  # Descripción de operación, permitir nulos
    descripcion_hospitalizacion = models.TextField(blank=True, null=True)  # Descripción de hospitalización, permitir nulos
    desmayos_ejercicio = models.BooleanField(blank=True, null=True)  # Permitir nulos, si ha tenido desmayos durante el ejercicio
    traumatismo_oseo = models.JSONField(blank=True, null=True)  # Especificar fractura, esguince, dislocación y en qué parte
    golpe_cabeza = models.TextField(blank=True, null=True)  # Descripción de golpes en la cabeza, permitir nulos
    alergias = models.JSONField(blank=True, null=True)  # Lista de alergias, permitir nulos
    enfermedad_actual = models.TextField(blank=True, null=True)  # Descripción de enfermedad actual, permitir nulos
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Historial Médico de Usuario {self.id}"     
    
class HistorialDeportivo(models.Model):
    miembro = models.OneToOneField(Miembro, on_delete=models.CASCADE, primary_key=True)
    deporte_actual = models.CharField(max_length=255, blank=True, null=True)  # Deporte actual, permite nulos
    actividad_fisica_reciente = models.JSONField(blank=True, null=True)  # JSON con campos {nombre, tiempo}, permite nulos
    lesion = models.JSONField(blank=True, null=True)
    def __str__(self):
        return f"Historial Deportivo de Usuario {self.id}" 