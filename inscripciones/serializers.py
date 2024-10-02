from rest_framework import serializers
from .models import GimnasioMixto, GimnasiaArtistica, Inscripcion, Asistencia 

class GimnasioMixtoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GimnasioMixto
        fields = '__all__'  # O especifica los campos que deseas incluir

class GimnasiaArtisticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GimnasiaArtistica
        fields = '__all__'  # O especifica los campos que deseas incluir

class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = '__all__'  # O especifica los campos que deseas incluir

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'  # O especifica los campos que deseas incluir

class ClasesSerializer(serializers.ModelSerializer):
    gimnasios_mixto = GimnasioMixtoSerializer(many=True)
    gimnasias_artistica = GimnasiaArtisticaSerializer(many=True)

    def to_representation(self, instance):
        return {
            'gimnasio_mixto': GimnasioMixtoSerializer(GimnasioMixto.objects.all(), many=True).data,
            'gimnasia_artistica': GimnasiaArtisticaSerializer(GimnasiaArtistica.objects.all(), many=True).data,
        }
        
class DatosInscripcionSerializer(serializers.ModelSerializer):
    gimnasio_mixto = GimnasioMixtoSerializer(read_only=True, allow_null=True)  # Anidamos GimnasioMixto
    gimnasia_artistica = GimnasiaArtisticaSerializer(read_only=True, allow_null=True)  # Anidamos GimnasiaArtistica

    class Meta:
        model = Inscripcion
        fields = ['acceso','gimnasio_mixto', 'gimnasia_artistica']
        
class DatosCredencial(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = ['id','clase']