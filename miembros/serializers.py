from rest_framework import serializers
from .models import Miembro, HistorialMedico, HistorialDeportivo,Visitantes
from inscripciones.serializers import DatosCredencial
import re

class MiembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Miembro
        fields = '__all__'  # O especifica los campos que deseas incluir
    # Validación de longitud máxima y mensajes personalizados
    
    paterno = serializers.CharField(
        max_length=100,
        error_messages={
            'max_length': 'El apellido paterno no puede tener más de 100 caracteres.',
        }
    )
    materno = serializers.CharField(
        max_length=100,
        error_messages={
            'max_length': 'El apellido materno no puede tener más de 100 caracteres.',
        }
    )
     
    
    
     
    

    
    # Validación de la edad
    

    def validate_curp(self, value):
        if not re.match(r'^[A-Z0-9]{18}$', value):
            raise serializers.ValidationError("El CURP debe tener 18 caracteres y deben ser letras mayusculas.")
        return value

    # Validación del formato del NSS (11 dígitos)
    def validate_nss(self, value):
        if value and not re.match(r'^\d{11}$', value):
            raise serializers.ValidationError("El número de seguridad social debe tener 11 dígitos.")
        return value

    # Validación del formato de número telefónico
    def validate_telefono_fijo(self, value):
        if value and not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("El número de teléfono fijo debe tener entre 10 y 15 dígitos.")
        return value

    def validate_celular(self, value):
        if value and not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("El número de celular debe tener entre 10 y 15 dígitos.")
        return value

    def validate_telefono_tutor(self, value):
        if value and not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("El número de teléfono del tutor debe tener entre 10 y 15 dígitos.")
        return value






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