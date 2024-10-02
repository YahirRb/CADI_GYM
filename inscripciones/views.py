from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
 
from  .models import Inscripcion,GimnasiaArtistica, GimnasioMixto
from .serializers import ClasesSerializer
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer

class Clases(APIView):
    def get(self, resquest):
        gimnasioMixto=GimnasioMixto.objects.all()
        gimnasiaArtistica= GimnasiaArtistica.objects.all()
        gimnasio_combinados_serializer = ClasesSerializer({
            'gimnasios_mixto': gimnasioMixto,
            'gimnasias_artistica': gimnasiaArtistica
        })
        
        # Retornar la respuesta
        return Response(gimnasio_combinados_serializer.data, status=HTTP_200_OK)
        