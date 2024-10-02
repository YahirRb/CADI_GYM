from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
from .models import Miembro
from inscripciones.models import Inscripcion
from pagos.models import Pagos
from .serializers import MiembroSerializer, HistorialDeportivoSerializer,HistorialMedicoSerializer,Credencial
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer

from cadi_gym.utils import supabase

class RegistroMiembro(APIView):
    def post(self, request):
        try:
            # Obtener datos del request
            datosMiembro = request.data.get('datos_miembro')
            historialMedico = request.data.get('historial_medico')
            historialDeportivo = request.data.get('historial_deportivo') 
            datosInscripcion = request.data.get('datos_inscripcion')

            # Serializar el miembro
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
                        inscripcion_data['fecha'] = datosMiembro['fecha']
                        

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


