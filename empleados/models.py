
from django.db import models

# Create your models here.

class Empleados(models.Model):
    nombre_completo=models.TextField()
    correo=models.EmailField()
    telefono=models.CharField(max_length=12)
    activo=models.BooleanField(default=True)
    