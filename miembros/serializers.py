from rest_framework import serializers
from .models import Miembro, HistorialMedico, HistorialDeportivo

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
