from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_403_FORBIDDEN
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from miembros.models import Miembro
from django.utils import timezone
from  .models import Inscripcion,GimnasiaArtistica, GimnasioMixto,Asistencia
from .serializers import ClasesSerializer
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer,AsistenciaSerializer
from pagos.models import Pagos
from cadi_gym.utils import enviar_correo
from empleados.notificaciones.notificaciones import  enviar_notificacion_a_alumno

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
            horario_inicio=request.data.get('horario_inicio')
            horario_fin=request.data.get('horario_fin')
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
                'fecha':fecha.date(),
                'horario_inicio':horario_inicio,
                'horario_fin':horario_fin,
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
            fecha_hoy = datetime.now().date()

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
            print(fecha_hoy)
            mensajes = []
            for pago in pagos_por_vencer: 
                print(pago)
                # Calcular los días restantes
                dias_restantes = (pago.proximo_pago - fecha_hoy).days
                miembro = pago.miembro  # Obtener el miembro asociado al pago
                inscripcion = pago.inscripcion
                print(inscripcion.id)
                clase_nombre =  inscripcion.clase  # Asegúrate de que `clase` y `nombre` están correctos
                
                if dias_restantes == 0 and pago.fecha_pago_realizado is None:
                    mensaje = f"Miembro {miembro.nombre}, hoy es su último día para realizar el pago por la clase {clase_nombre}."
                else:
                    mensaje = f"Miembro {miembro.nombre}, le quedan {dias_restantes} días para realizar su pago por la clase {clase_nombre}."
                
                # Agregar el mensaje a la lista
                mensajes.append(mensaje)
                print(mensajes)
                enviar_notificacion_a_alumno(miembro.num_control,mensaje)
                
                enviar_correo(
                    destinatario=miembro.correo,
                    asunto='Recordatorio de pago',
                    mensaje=mensaje)
                    
            
            # Devolver los mensajes generados
            return Response(mensajes,status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error al procesar las notificaciones."}, status=HTTP_400_BAD_REQUEST)


class InscripcionesMiembro(APIView):
    def get(self,request):
        try:
            num_control=request.GET.get('num_control')
            inscripciones= Inscripcion.objects.filter(miembro=num_control,acceso=True)
            serializer=InscripcionSerializer(inscripciones,many=True)
            return Response(data=serializer.data,status=HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)

class BajaInscripcion(APIView):
    def put(self,request):
        try:
            lista_id=request.data.get('id_inscripcion')
            fecha_hoy = datetime.now().date()
            
            
            for id in lista_id:
                inscripcion=Inscripcion.objects.get(id=id,acceso=True)
                pagos=Pagos.objects.filter(inscripcion=id, estado='pendiente')
                for pago in pagos:
                    if fecha_hoy < pago.proximo_pago:
                        
                        inscripcion.acceso=False
                        inscripcion.save()
                        pago.estado='cancelado'
                        pago.save()
                    else:
                        return Response(data=f"No puede dar de baja la clase {inscripcion.clase}",status=HTTP_400_BAD_REQUEST)
            
            
            return Response(data="Baja exitosa",status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)

class AsistenciaDiaActual(APIView):
    def get(self,request):
        try:
            fecha_hoy = datetime.now().date()
            asistencias=Asistencia.objects.filter(fecha=fecha_hoy)
            datos_asistencias = []
            for asistencia in asistencias:
                inscripcion=asistencia.inscripcion
                datos_inscripcion=Inscripcion.objects.get(id= inscripcion.id)
                print(inscripcion.miembro)
                miembro= Miembro.objects.get(num_control=datos_inscripcion.miembro.num_control)
                datos_asistencias.append({
                    'hora': asistencia.hora,
                    'fecha': asistencia.fecha,
                    'nombre':miembro.nombre,
                    'paterno':miembro.paterno,
                    'materno':miembro.materno,
                    'clase':datos_inscripcion.clase,
                    'modalidad':datos_inscripcion.modalidad
                })
             
            return Response(data=datos_asistencias,status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST) 
        
class AsistenciasFiltro(APIView):
    def get(self,request):
        try:
            mesMinimo = request.GET.get('mes_minimo')
            mesMaximo = request.GET.get('mes_maximo')
            anio = request.GET.get('anio')
            fechaMinima = request.GET.get('fecha_minima')
            fechaMaxima = request.GET.get('fecha_maxima') 
            print(fechaMaxima)
            filtros = {} 
            # Filtro para mes (rango de meses)
            if mesMinimo and mesMaximo and anio:
                # Filtrar por rango de meses dentro de un año específico
                filtros['fecha__month__range'] = (mesMinimo, mesMaximo)
                filtros['fecha__year'] = anio  # También filtramos por año específico

            # Filtro para rango de fechas
            if fechaMinima and fechaMaxima:
                # Filtrar por rango de fechas
                filtros['fecha__range'] = (fechaMinima, fechaMaxima)
            datos_asistencias = []
            if filtros:
                
                asistencias = Asistencia.objects.filter(**filtros)
                
                for asistencia in asistencias:
                    inscripcion=asistencia.inscripcion
                    datos_inscripcion=Inscripcion.objects.get(id= inscripcion.id)
                    print(inscripcion.miembro)
                    miembro= Miembro.objects.get(num_control=datos_inscripcion.miembro.num_control)
                    datos_asistencias.append({
                        'hora': asistencia.hora,
                        'fecha': asistencia.fecha,
                        'nombre':miembro.nombre,
                        'paterno':miembro.paterno,
                        'materno':miembro.materno,
                        'clase':datos_inscripcion.clase,
                        'modalidad':datos_inscripcion.modalidad
                    })  
                
            return Response(data=datos_asistencias,status=HTTP_200_OK)
            
        except Exception as e:
            print(f"Ocurrió un error: {e}")  # Para propósitos de depuración
            return Response(data="Ocurrió un error", status=HTTP_400_BAD_REQUEST)






