from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
from .models import Miembro,Visitantes
from inscripciones.models import Inscripcion
from pagos.models import Pagos
from .serializers import MiembroSerializer, HistorialDeportivoSerializer,HistorialMedicoSerializer,Credencial,VisitanteSerializer
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer
from datetime import datetime, timedelta
from django.utils import timezone 
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
import jwt
from cadi_gym.settings import SECRET_KEY
from cadi_gym.utils import enviar_correo

from cadi_gym.utils import supabase

User = get_user_model()

class RegistroMiembro(APIView):
    def post(self, request):
        try:
            # Obtener datos del request
            datosMiembro = request.data.get('datos_miembro')
            historialMedico = request.data.get('historial_medico')
            historialDeportivo = request.data.get('historial_deportivo') 
            datosInscripcion = request.data.get('datos_inscripcion')
            fecha_str=datosMiembro['fecha']
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            # Serializar el miembro
            curp= datosMiembro['curp']
            password= curp[:10]
            print(password)
            serializerMiembro = MiembroSerializer(data=datosMiembro)

            if serializerMiembro.is_valid():
                # Guardar el miembro
                miembro = serializerMiembro.save()
                num_control = miembro.num_control  # Obtener el identificador del miembro

                # Asignar ID de miembro a historiales
                historialMedico['miembro'] = num_control
                historialDeportivo['miembro'] = num_control

                # Serializar historiales
                serializerMedico = HistorialMedicoSerializer(data=historialMedico)
                serializerDeportivo = HistorialDeportivoSerializer(data=historialDeportivo)

                # Validar historiales
                if all([serializerMedico.is_valid(), serializerDeportivo.is_valid()]):
                    # Guardar historiales
                    serializerMedico.save()
                    serializerDeportivo.save()

                    # Procesar cada inscripción en la lista
                    for inscripcion_data in datosInscripcion: 
                        # Asignar ID de miembro a cada inscripción
                        inscripcion_data['miembro'] = num_control
                        modalidad=inscripcion_data['modalidad']
                        print('segundo')
                        print(modalidad)
                        
                        inscripcion_data['fecha'] = datosMiembro['fecha']
                        if modalidad == 'Semana':
                            proximo_pago= fecha + relativedelta(weeks=1)
                        elif modalidad =='Quincena':
                            proximo_pago= fecha + timedelta(days=15)
                        elif modalidad == 'Mes' or modalidad == 'Mes (de 5 a 6 años)' or modalidad == 'Mes (7 años en adelante)':
                            proximo_pago= fecha + relativedelta(months=1)
                        elif modalidad == 'Trimestre':
                            proximo_pago= fecha + relativedelta(months=3)
                        elif modalidad == '6 meses':
                            proximo_pago= fecha + relativedelta(months=6) 
                        inscripcion_data['proximo_pago']=proximo_pago.date()
                        # Serializar inscripción
                        serializerInscripcion = InscripcionSerializer(data=inscripcion_data)

                        if serializerInscripcion.is_valid():
                            print("si entra")
                            inscripcion = serializerInscripcion.save()  # Guardar inscripción

                            # Preparar datos del pago realizado
                            datosPagoRealizado = {
                                'fecha_pago_realizado': datosMiembro['fecha'],
                                'estado': 'pagado',
                                'inscripcion': inscripcion.id,
                                'miembro': num_control,
                                'monto': inscripcion_data['monto'],  # Obtener el monto de la inscripción
                                'proximo_pago': inscripcion_data['proximo_pago']  # Obtener la fecha del próximo pago
                            }

                            # Serializar el pago realizado
                            serializerPagoRealizado = PagosSerializer(data=datosPagoRealizado)

                            if serializerPagoRealizado.is_valid():
                                print("si guarda el pago")
                                # Guardar el pago realizado
                                serializerPagoRealizado.save()
                            else:
                                return Response({"errors": serializerPagoRealizado.errors}, status=HTTP_400_BAD_REQUEST)

                            # Preparar datos del pago pendiente
                            datosPagoPendiente = {
                                'fecha_pago_realizado': None,  # No se ha realizado el pago
                                'estado': 'pendiente',
                                'inscripcion': inscripcion.id,
                                'miembro': num_control,
                                'monto': inscripcion_data['costo'],  # Puede ser el mismo monto
                                'proximo_pago': inscripcion_data['proximo_pago']  # Usar la misma fecha
                            }

                            # Serializar el pago pendiente
                            serializerPagoPendiente = PagosSerializer(data=datosPagoPendiente)

                            if serializerPagoPendiente.is_valid():
                                # Guardar el pago pendiente
                                serializerPagoPendiente.save()
                                
                            else:
                                return Response({"errors": serializerPagoPendiente.errors}, status=HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"errors": serializerInscripcion.errors}, status=HTTP_400_BAD_REQUEST)
                    """
                    enviar_correo(
                        destinatario=datosMiembro['correo'],
                        asunto='Recordatorio de pago',
                        mensaje="mensaje")
                    """
                    return Response({"message": "Miembro registrado con éxito junto con historiales, inscripciones y pagos."}, status=HTTP_201_CREATED)
                else:
                    # Recopilar errores de validación
                    errors = {
                        "historial_medico": serializerMedico.errors,
                        "historial_deportivo": serializerDeportivo.errors,
                    }
                    return Response(errors, status=HTTP_400_BAD_REQUEST)
            else:
                # Error en la validación del miembro
                return Response(serializerMiembro.errors, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {e}")  # Para propósitos de depuración
            return Response({"error": "Ocurrió un error durante el registro."}, status=HTTP_500_INTERNAL_SERVER_ERROR)

class DatosMiembro(APIView):
    def get(self,request):
        try:
            id= request.GET.get('user_id')
            datosMiembro = Miembro.objects.get(num_control=id)
            inscripciones= Inscripcion.objects.filter(miembro=datosMiembro.num_control)
            if datosMiembro.foto:
                foto_url = supabase.storage.from_('cadi_gym').get_public_url(datosMiembro.foto)  # Esto mostrará la URL de la imagen
            else:
                foto_url=None
            
            datos = {
                "num_control": datosMiembro.num_control,
                "nombre": datosMiembro.nombre,
                "apellidos": datosMiembro.apellidos,
                "foto":foto_url,
                "inscripciones": []
            }
            for inscripcion in inscripciones:  
                pago=Pagos.objects.filter(inscripcion=inscripcion.id,estado='pendiente').latest('proximo_pago')
                datos["inscripciones"].append({
                        "clase": inscripcion.clase,
                        "idInscripcion": inscripcion.id,
                        "vigencia":pago.proximo_pago
                    }) 
            return Response(data=datos, status=HTTP_200_OK) 
        except Miembro.DoesNotExist:
            print("no existe")
        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error durante el registro."}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        
class  FotoCredencial(APIView):
    def post(self, request): 
        user_id = request.data.get('user_id')
        
        print(user_id)
        foto = request.FILES.get('foto')  
        if not foto:
            return Response({"error": "No se ha proporcionado ninguna imagen."}, status= HTTP_400_BAD_REQUEST)
        miembro = Miembro.objects.get(num_control=user_id)
        # Define la ruta donde se almacenará la imagen en Supabase
        path_on_supastorage = f"images/{miembro.num_control}.png"  # Puedes personalizar la ruta si lo deseas

        try:
            # Sube la imagen al bucket usando el contenido del archivo
            res = supabase.storage.from_('cadi_gym').upload(
                path_on_supastorage,
                file=foto.read(),  # Lee el contenido del archivo
                file_options={"content-type": foto.content_type}  # Establece el tipo de contenido
            )

             
            # Actualiza el modelo miembro para guardar la ruta de la imagen
              # Asegúrate de que el CURP existe en la base de datos
            miembro.foto = path_on_supastorage  # Guarda la ruta de la imagen en el campo 'foto'
            miembro.save()  # Guarda los cambios en la base de datos

            return Response({"message": f"Imagen '{foto.name}' subida exitosamente!", "path": path_on_supastorage}, status= HTTP_201_CREATED)

        except Exception as e:
            # Manejo de errores si la subida falla
            return Response({"error": str(e)}, status= HTTP_400_BAD_REQUEST)

class RegistroVisitante(APIView):
    def post(self,request):
        try:
            fecha_actual = datetime.now().date() 
            nombre=request.data.get('nombre')
            apellidos=request.data.get('apellidos')
            correo=request.data.get('correo')
            celular=request.data.get('celular')
            datos_visitante={
                'nombre':nombre,
                'apellidos':apellidos,
                'correo':correo,
                'celular':celular
            }
            datos_pago={
                
            }
            nuevo_visitante=VisitanteSerializer(data=datos_visitante)
            if nuevo_visitante.is_valid():
                nuevo_visitante.save()
                return Response(data="Visitante registrado",status=HTTP_201_CREATED)
            else:
                return Response(data="Error al registrar visitante",status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
            
class ListarVisitantes(APIView):
    def get(self,request):
        try:
            
            visitantes=Visitantes.objects.all()
            serializer=VisitanteSerializer(visitantes,many=True)
            
            return Response(data=serializer.data,status=HTTP_200_OK)
        except Exception as e:
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        
class SuspenderMiembro(APIView):
    def put(self,request):
        try:
            id_miembro=request.data.get('num_control')
            inscripciones=Inscripcion.objects.filter(miembro=id_miembro)
            usuario=User.objects.get(num_control=id_miembro)
            pagos=Pagos.objects.filter(miembro=id_miembro,estado='pendiente' )
            usuario.is_active=False
            for inscripcion in inscripciones:
                
                inscripcion.acceso=False
                inscripcion.save() 
            for pago in pagos:
                pago.estado='cancelado'
                pago.save()
            
            usuario.save() 
            return Response(data="Baja exitosa",status=HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        
class RegistroTemporal(APIView):
    def get(self,request):
        try:
            payload = {
                'num_control': 13,  # Puedes incluir los datos que necesites
                'exp': timezone.now() + timedelta(minutes=5)  # Expiración de 5 minutos
            }

            # Crear el token
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            print("Token JWT:", token)
        except Exception as e:
            print(e)
        return Response("")
        
        
        
        
        