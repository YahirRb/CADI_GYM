from django.db import models
from miembros.models import Miembro

# Create your models here.
class GimnasioMixto(models.Model):
    modalidad = models.CharField(max_length=50)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Modalidad: {self.modalidad} - Costo: {self.costo}"
    
    
class GimnasiaArtistica(models.Model):
    modalidad = models.CharField(max_length=50)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Modalidad: {self.modalidad} - Costo: {self.costo}"
    
class Inscripcion(models.Model):
    fecha = models.DateField()  # Fecha de inscripción
    acceso = models.BooleanField(default=True)  # Indica si el miembro tiene acceso
    costo = models.DecimalField(max_digits=10, decimal_places=2)  # Monto de inscripción
    modalidad = models.CharField(max_length=50)
    clase = models.TextField(blank=True, null=True )
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE)  # Relación con el miembro

    def __str__(self):
        return f"Inscripción de {self.miembro.nombre} - Fecha: {self.fecha}"

class Asistencia(models.Model):
    fecha = models.DateField()  # Fecha de la asistencia
    hora = models.TimeField()  # Hora de la asistencia
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)  # Relación con la inscripción

    def __str__(self):
        return f"Asistencia - Fecha: {self.fecha} - Hora: {self.hora} - Inscripción: {self.inscripcion.miembro.nombre}"