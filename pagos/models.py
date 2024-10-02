from miembros.models import Miembro
from inscripciones.models import Inscripcion
from django.db import models

# Create your models here.
class Pagos(models.Model):
    estado = models.CharField(max_length=20, default='pendiente') 
    fecha_pago_realizado= models.DateField(null=True, blank=True) 
    proximo_pago = models.DateField()  # Fecha del próximo pago
    monto = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)  # Monto del pago
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE)  # Relación con el miembro
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)  # Relación con la inscripción

    def __str__(self):
        return f"Pago de {self.miembro.nombre} - Monto: {self.monto} - Estado: {self.estado}"