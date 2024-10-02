from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
from .models import Pagos
from miembros.models import Miembro
from inscripciones.models import Inscripcion 
from .serializers import PagosSerializer,PagosPendientes
from inscripciones.serializers import InscripcionSerializer
from datetime import date

class PagosPendientesUsuario(APIView):
    def get(self,request):
        try:
            usuario= Miembro.objects.get(correo=request.GET.get('user_id')) 
            fecha_actual = date.today()  
            pagos = Pagos.objects.filter(miembro=usuario.num_control, estado='pendiente')
            pagos_validos = []

            for pago in pagos:
                inscripcion = pago.inscripcion
                print(f"Fecha de inscripción: {inscripcion.fecha}")
                print(pago.monto)
                # Verifica la modalidad y la fecha del próximo pago
                if inscripcion.modalidad == 'Mes' and pago.proximo_pago >= fecha_actual:
                    pago.monto=500
                    pagos_validos.append(pago)
                elif inscripcion.modalidad == 'Mes (de 5 a 6 años)' and pago.proximo_pago >= fecha_actual:
                    print("inscripcion niño")
                    pago.monto=680
                    pagos_validos.append(pago)
                elif inscripcion.modalidad == 'Mes (7 años en adelante)' and pago.proximo_pago >= fecha_actual:
                    print("inscripcion adulto")
                    pago.monto=760
                    pagos_validos.append(pago)
                elif pago.proximo_pago < fecha_actual:
                    pago.monto=pago.monto+50
                    pagos_validos.append(pago)
                else:
                    pagos_validos.append(pago)

            # Serializa solo los pagos válidos
            serializer = PagosSerializer(pagos_validos, many=True)
            return Response(data=serializer.data)

        except Miembro.DoesNotExist as e:
            print(e)
            return Response({"error": "Usuario no encontrado"}, status=404)
        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error en la solicitud"}, status=500)