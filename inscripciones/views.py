from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_403_FORBIDDEN
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from  .models import Inscripcion,GimnasiaArtistica, GimnasioMixto,Asistencia
from .serializers import ClasesSerializer
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer,AsistenciaSerializer
from pagos.models import Pagos
from cadi_gym.utils import enviar_correo

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
            print(miembro)
            print(id_inscripcion)
            print(fecha)
            print(hora)
            inscripcion=Inscripcion.objects.get(id=id_inscripcion)
            print(inscripcion)
            ultimoPago=Pagos.objects.filter(inscripcion=id_inscripcion,estado='pendiente').latest('proximo_pago')
            datos_asistencia = {
                'miembro': miembro,  # Asegúrate que coincida con el campo en el modelo
                'inscripcion': inscripcion.id,  # Relacionas la inscripción con el registro
                'fecha': fecha,
                'hora': hora
            }

            # Pasar los datos al serializador
            asistencia_serializer = AsistenciaSerializer(data=datos_asistencia)
            proximo_pago = ultimoPago.proximo_pago

            # Calcular la fecha límite (proximo_pago + 5 días)
            fecha_limite = proximo_pago + timedelta(days=5)

            # Obtener la fecha actual
            fecha_actual = datetime.now().date()
            
            if inscripcion.acceso :
                if fecha_limite < fecha_actual:
                    inscripcion.acceso=False
                    inscripcion.save()
                    return Response(data="No tienes acceso",status=HTTP_403_FORBIDDEN)
                elif asistencia_serializer.is_valid():
                    asistencia_serializer.save()
                    return Response(data="Asistencia registrada",status=HTTP_201_CREATED)
                else:
                    print(asistencia_serializer.errors)
                    return Response(data="Error al registrar la asistencia",status=HTTP_400_BAD_REQUEST)
                    
            else:
                return Response(data="No tienes acceso",status=HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        
class CambioModalidad(APIView):
    def put(self,request):
        try: 
            id_miembro=request.data.get('num_control')
            id_inscripcion=request.data.get('id_inscripcion')
            fecha_str=request.data.get('fecha')
            modalidad=request.data.get('modalidad')
            costo = request.data.get('costo')
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            inscripcion=Inscripcion.objects.get(id=id_inscripcion)
            inscripcion.modalidad=modalidad
            inscripcion.costo=costo
            pagos=Pagos.objects.filter(inscripcion=id_inscripcion, estado='pendiente' )
            if pagos.exists():
                for pago in pagos:
                    pago.monto = costo

                    if modalidad == 'Semana':
                        proximo_pago = fecha + relativedelta(weeks=1)
                    elif modalidad == 'Quincena':
                        proximo_pago = fecha + timedelta(days=15)
                    elif modalidad == 'Mes' or modalidad == 'Mes (de 5 a 6 años)' or modalidad == 'Mes (7 años en adelante)':
                        proximo_pago = fecha + relativedelta(months=1)
                    elif modalidad == 'Trimestre':
                        proximo_pago = fecha + relativedelta(months=3)
                    elif modalidad == '6 meses':
                        proximo_pago = fecha + relativedelta(months=6)

                    pago.proximo_pago = proximo_pago.date()
                    pago.save()
            
            inscripcion.save()
            return Response(data="Cambio realizado existosamente",status=HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        
class RegistrarInscripcion(APIView):
    def post(self,request):
        try:
            num_control=request.data.get('num_control')
            clase=request.data.get('clase')
            modalidad=request.data.get('modalidad')
            costo=request.data.get('costo')
            monto=request.data.get('monto_total')
            fecha_str = request.data.get('fecha')  # Asegúrate de que la fecha está en un formato que puedas analizar
            print(fecha_str)
# Convertir la fecha desde una cadena a un objeto datetime
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            print(fecha)
            nueva_fecha = fecha + relativedelta(months=1)

            print(nueva_fecha.date())
            existe=Inscripcion.objects.filter(miembro=num_control, clase=clase, acceso=True )
            if existe.exists():
                return Response(data='Ya se encuentra registrado',status=HTTP_400_BAD_REQUEST)
            
            datos_inscripcion={
                'miembro':num_control,
                'clase':clase,
                'modalidad':modalidad,
                'costo':costo,
                'fecha':fecha.date()
            }
            
            serializerInscripcion=InscripcionSerializer(data=datos_inscripcion)
            if serializerInscripcion.is_valid():
                inscripcion=serializerInscripcion.save()
                datos_pago={
                    'miembro':num_control,
                    'estado':'pagado',
                    'fecha_pago_realizado':fecha.date(),
                    'proximo_pago':fecha.date(),
                    'monto':monto,
                    'inscripcion':inscripcion.id
                }
                datos_proximo_pago={
                    'miembro':num_control,
                    'estado':'pendiente',
                    'fecha_pago_realizado':fecha.date(),
                    'proximo_pago':nueva_fecha.date(),
                    'monto':costo,
                    'inscripcion':inscripcion.id
                }
                serializerPago=PagosSerializer(data=datos_pago)
                serializerProximoPago=PagosSerializer(data=datos_proximo_pago)
                if serializerPago.is_valid() and serializerProximoPago.is_valid():
                    serializerPago.save()
                    serializerProximoPago.save()
                    print("si")
                else:
                    print("error pago",serializerPago.errors)
                    print("error proximo pago", serializerProximoPago.errors)
            else:
                print(serializerInscripcion.errors)
            return Response("")
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        
        
class NotificarPagos(APIView):
    def get(self, request):
        try:
            # Obtener la fecha de hoy
            fecha_hoy = timezone.now().date()

            # Definir las fechas de vencimiento (hoy, +1 día, +3 días, +5 días)
            fechas_vencimiento = [
                fecha_hoy,
                fecha_hoy + timedelta(days=1),
                fecha_hoy + timedelta(days=3),
                fecha_hoy + timedelta(days=5),
            ]

            # Filtrar los pagos pendientes cuya fecha de próximo pago esté en las fechas de vencimiento
            pagos_por_vencer = Pagos.objects.filter(
                proximo_pago__in=fechas_vencimiento,
                estado='pendiente'  # Solo los pagos que no han sido realizados
            )

            mensajes = []
            for pago in pagos_por_vencer: 
                # Calcular los días restantes
                dias_restantes = (pago.proximo_pago - fecha_hoy).days
                miembro = pago.miembro  # Obtener el miembro asociado al pago
                inscripcion = pago.inscripcion
                print(inscripcion.id)
                clase_nombre =  inscripcion.clase  # Asegúrate de que `clase` y `nombre` están correctos
                
                if dias_restantes == 0 and pago.pago_realizado is None:
                    mensaje = f"Miembro {miembro.nombre}, hoy es su último día para realizar el pago por la clase {clase_nombre}."
                else:
                    mensaje = f"Miembro {miembro.nombre}, le quedan {dias_restantes} días para realizar su pago por la clase {clase_nombre}."
                enviar_correo(
                    destinatario=miembro.correo,
                    asunto='Recordatorio de pago',
                    mensaje=mensaje)
                # Agregar el mensaje a la lista
                mensajes.append(mensaje)

            

            # Devolver los mensajes generados
            return Response(mensajes, status=200)

        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error al procesar las notificaciones."}, status=400)
