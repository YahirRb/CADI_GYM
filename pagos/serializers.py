from rest_framework import serializers
from .models import Pagos
from inscripciones.serializers import InscripcionSerializer,DatosInscripcionSerializer

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'  # O especifica los campos que deseas incluir

class PagosPendientes(serializers.ModelSerializer):
    # Incluye el serializador de Inscripcion
    inscripcion = InscripcionSerializer(read_only=True)

    # Campos adicionales para clase y modalidad
    clase = serializers.CharField(source='inscripcion.clase', read_only=True)
    modalidad = serializers.CharField(source='inscripcion.modalidad', read_only=True)

    class Meta:
        model = Pagos
        fields = ['estado', 'proximo_pago', 'monto', 'miembro', 'inscripcion', 'clase', 'modalidad']
