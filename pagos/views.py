from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_404_NOT_FOUND
from .models import Pagos
from miembros.models import Miembro
from inscripciones.models import Inscripcion 
from .serializers import PagosSerializer,PagosPendientes
from inscripciones.serializers import InscripcionSerializer
from datetime import date

class PagosPendientesUsuario(APIView):
    def get(self,request):
        try:
            num_control=request.GET.get('user_id')
            usuario= Miembro.objects.get(num_control=request.GET.get('user_id')) 
            fecha_actual = date.today()  
            pagos = Pagos.objects.filter(miembro=num_control, estado='pendiente')
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

class RegistrarPago(APIView):
    def post(self,request):
        try:
            proximo_pago= request.data.get('proximo_pago')
            fecha_pago= request.data.get('fecha_pago')
            monto = request.data.get('monto')
            id_pago = request.data.get('id_pago')
            pago = Pagos.objects.get(id=id_pago)
            pago.fecha_pago_realizado=fecha_pago
            pago.estado='pagado'
            miembro= pago.miembro
            inscripcion=pago.inscripcion
            datos_inscripcion= Inscripcion.objects.get(id= inscripcion.id)
            
            datos_inscripcion.acceso=True
            
            nuevo_pago={
                'fecha_pago_realizado': None,  # No se ha realizado el pago
                'estado': 'pendiente',
                'inscripcion': inscripcion.id,
                'miembro':  miembro.num_control,
                'monto': pago.monto,  # Puede ser el mismo monto
                'proximo_pago': proximo_pago  # Usar la misma fecha
            }
            
            serializer= PagosSerializer(data=nuevo_pago)
            
            if serializer.is_valid():
                pago.save()
                datos_inscripcion.save()
                serializer.save()
            else:
                return Response(data="Datos de pago incorrectos",status=HTTP_404_NOT_FOUND)
            return Response(data="Pago registrado",status=HTTP_200_OK)
        except Pagos.DoesNotExist:
            return Response(data="Ocurrio un error",status=HTTP_404_NOT_FOUND)
        except Inscripcion.DoesNotExist:
            return Response(data="Ocurrio un error",status=HTTP_404_NOT_FOUND)
        except Exception as e:
            property(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        