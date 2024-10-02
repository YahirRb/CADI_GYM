from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
from datetime import datetime, timedelta
from  .models import Inscripcion,GimnasiaArtistica, GimnasioMixto,Asistencia
from .serializers import ClasesSerializer
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer,AsistenciaSerializer
from pagos.models import Pagos

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
        

class RegistrarAsistencia(APIView):
    def post(self,request):
        try:
            miembro= request.data.get('num_control')
            id_inscripcion= request.data.get('id_inscripcion')
            fecha=request.data.get('fecha')
            hora=request.data.get('hora')
            inscripcion=Inscripcion.objects.get(id=id_inscripcion)
            ultimoPago=Pagos.objects.filter(inscripcion=id_inscripcion,estado='pendiente').latest('proximo_pago')
             # Obtener la fecha de proximo_pago
            proximo_pago = ultimoPago.proximo_pago

            # Calcular la fecha límite (proximo_pago + 5 días)
            fecha_limite = proximo_pago + timedelta(days=5)

            # Obtener la fecha actual
            fecha_actual = datetime.now().date()
            if fecha_limite < fecha_actual:
                inscripcion.acceso=False
                inscripcion.save()
            # Comparar la fecha límite con la fecha actual
            if fecha_actual <= fecha_limite:
                print("Tienes tiempo para pagar.")
            else:
                print("La fecha de pago ha pasado.") 
            if inscripcion.acceso :
                print("pasas")
            else:
                print('no pasas')
        except Exception as e:
            print(e)
        return Response("")