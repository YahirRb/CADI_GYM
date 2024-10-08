from rest_framework import serializers
from .models import Miembro, HistorialMedico, HistorialDeportivo,Visitantes
from inscripciones.serializers import DatosCredencial

class MiembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Miembro
        fields = '__all__'  # O especifica los campos que deseas incluir

class HistorialMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialMedico
        fields = '__all__'  # O especifica los campos que deseas incluir

class HistorialDeportivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialDeportivo
        fields = '__all__'  # O especifica los campos que deseas incluir
        
class Credencial(serializers.ModelSerializer):
    inscripcion = DatosCredencial(many=True, allow_null=True)
    class Meta:
        model = Miembro
        fields = ['num_control','nombre','apellidos','inscripcion']
        
class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitantes
        fields = '__all__'
        
class DatosCompletos(serializers.ModelSerializer):
    historial_medico = HistorialMedicoSerializer(read_only=True)
    historial_deportivo = HistorialDeportivoSerializer(read_only=True)

    class Meta:
        model = Miembro
        fields = '__all__' 