from rest_framework import serializers
from .models import Empleados

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleados
        fields = '__all__'  # O especifica los campos que deseas incluir
