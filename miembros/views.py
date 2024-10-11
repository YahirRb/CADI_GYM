from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND
from .models import Miembro,Visitantes,HistorialMedico,HistorialDeportivo
from inscripciones.models import Inscripcion
from pagos.models import Pagos
from login.models import TokenUtilizado
from .serializers import MiembroSerializer, HistorialDeportivoSerializer,HistorialMedicoSerializer,Credencial,VisitanteSerializer,DatosCompletos
from pagos.serializers import PagosSerializer
from inscripciones.serializers import InscripcionSerializer
from datetime import datetime, timedelta
from django.utils import timezone 
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from cadi_gym.settings import SECRET_KEY
from cadi_gym.utils import enviar_correo 
from cadi_gym.utils import supabase
import environ
#from firebase_admin import storage
#from cadi_gym.firebase_config import bucket

env = environ.Env()
environ.Env.read_env()

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
            inscripciones=[]
            serializerMiembro = MiembroSerializer(data=datosMiembro)
            if serializerMiembro.is_valid():
                
                miembro = serializerMiembro.save()
                num_control = miembro.num_control
                
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
                            inscripciones.append({
                                "clase": inscripcion.clase,
                                "idInscripcion": inscripcion.id,
                                "vigencia":inscripcion_data['proximo_pago']
                            })
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
                                print(serializerPagoRealizado.errors)
                                return Response({"error": serializerPagoRealizado.errors}, status=HTTP_400_BAD_REQUEST)

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
                                print(serializerPagoPendiente.errors)
                                
                                return Response({"error": serializerPagoPendiente.errors}, status=HTTP_400_BAD_REQUEST)
                        else:
                            print(serializerInscripcion.errors)
                            return Response({"error": serializerInscripcion.errors}, status=HTTP_400_BAD_REQUEST)
                    """
                    enviar_correo(
                        destinatario=datosMiembro['correo'],
                        asunto='Recordatorio de pago',
                        mensaje="mensaje")
                    """
                    usuario = {
                        "correo": password,
                        "password": password,
                        "num_control": num_control,
                        "inscripciones":inscripciones
                    }
                    return Response(data=usuario, status=HTTP_201_CREATED)
                else:
                    # Recopilar errores de validación
                    errors = {
                        "historial_medico": serializerMedico.errors,
                        "historial_deportivo": serializerDeportivo.errors,
                    }
                    print(errors)
                    return Response({"error": errors}, status=HTTP_400_BAD_REQUEST)
            else:
                # Error en la validación del miembro
                errores_formateados = []

                # Recorrer los errores del serializador
                for campo, errores in serializerMiembro.errors.items():
                    for error in errores:
                        # Agregar cada campo y error al formato deseado
                        errores_formateados.append(f"{campo} = {str(error)}")

                # Unir todos los errores en un solo string separado por "|"
                errores_str = " | ".join(errores_formateados)
                return Response({"error": errores_str}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {e}")  # Para propósitos de depuración
            return Response({"error": f"Ocurrió un error durante el registro. {e}"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

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
                "apellidos": f"{datosMiembro.paterno} {datosMiembro.materno}", 
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
            return Response(data="El usuario no existe",status=HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error durante el registro."}, status=HTTP_500_INTERNAL_SERVER_ERROR)
"""     
class  FotoCredencial(APIView):
    def post(self, request): 
        try:
            user_id = request.data.get('user_id')
            foto = request.FILES.get('foto')
            if not foto:
                return Response({"error": "No se ha proporcionado ninguna imagen."}, status= HTTP_400_BAD_REQUEST)
            miembro = Miembro.objects.get(num_control=user_id)
            # Define la ruta donde se almacenará la imagen en Supabase
            blob_name = f'images/{user_id}.png'  # Puedes ajustar la ruta según sea necesario

            # Crea el blob y sube el archivo
            blob = bucket.blob(blob_name)
            blob.upload_from_file(foto)

            # Obtiene la URL del archivo subido
            blob.make_public()
            image_url = blob.public_url
            print(image_url)

             
            # Actualiza el modelo miembro para guardar la ruta de la imagen
              # Asegúrate de que el CURP existe en la base de datos
            miembro.foto = blob_name  # Guarda la ruta de la imagen en el campo 'foto'
            miembro.save()  # Guarda los cambios en la base de datos

            return Response({"message": f"Imagen '{foto.name}' subida exitosamente!", "path": blob_name}, status= HTTP_201_CREATED)

        except Exception as e:
            # Manejo de errores si la subida falla
            return Response({"error": str(e)}, status= HTTP_400_BAD_REQUEST)
""" 

class  FotoCredencial(APIView):
    def post(self, request): 
        user_id = request.data.get('user_id')
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
            fecha_hoy = datetime.now().date()
            nombre=request.data.get('nombre')
            paterno=request.data.get('paterno')
            materno=request.data.get('materno')
            correo=request.data.get('correo')
            costo=request.data.get('costo')
            clase=request.data.get('clase')
            celular=request.data.get('celular')
            datos_visitante={
                'nombre':nombre,
                'paterno':paterno,
                'materno':materno,
                'correo':correo,
                'celular':celular,
                'clase':clase,
                'costo':costo,
                'ultima_visita':fecha_hoy
            }
            
            nuevo_visitante=VisitanteSerializer(data=datos_visitante)
            if nuevo_visitante.is_valid():
                visitante=nuevo_visitante.save()
                
                datos_pago={
                    "estado":"pagado",
                    "fecha_pago_realizado":fecha_hoy,
                    "proximo_pago":fecha_hoy,
                    "monto":costo,
                    "visitante":visitante.id
                }
                
                serializer= PagosSerializer(data=datos_pago)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response(data="Visitante registrado",status=HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)
                
            else:
                print("error")
                print(nuevo_visitante.errors)
                return Response(data=nuevo_visitante.errors,status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
            
class ListarVisitantes(APIView):
    def get(self,request):
        try:
            
            visitantes=Visitantes.objects.all()
            serializer=VisitanteSerializer(visitantes,many=True)
            
            return Response(data=serializer.data,status=HTTP_200_OK)
        except Exception as e:
            print(e)
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
        
class EnlaceTemporal(APIView):
    def get(self,request):
        try:
            
            correo=request.GET.get('correo')
            payload = {  
                'exp': timezone.localtime(timezone.now()) + timedelta(hours=12)  # Expiración de 12 horas
            } 
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            enviar_correo(
                destinatario=correo,
                asunto='Enlace de registro',
                mensaje=f"{env.str('URL_REGISTRO_TEMPORAL')}{token}")
            
            return Response(data="Correo enviado",status=HTTP_200_OK)
        except ExpiredSignatureError:
                # El token ha expirado
                return Response(data="El token ha expirado", status=HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
                # El token es inválido
                return Response(data="El token es inválido", status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)
        

class RegistroTemporal(APIView):
    def post(self, request):
        try:
            token=request.data.get('token')
            
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if TokenUtilizado.objects.filter(token=token).exists():
                return Response(data="El token ya ha sido utilizado", status=HTTP_401_UNAUTHORIZED)

            # Si es válido, almacénalo como utilizado
            TokenUtilizado.objects.create(token=token)
            
            #foto = request.FILES.get('foto')
            
            datosMiembro = request.data.get('datos_miembro')
            historialMedico = request.data.get('historial_medico')
            historialDeportivo = request.data.get('historial_deportivo') 
            datosInscripcion = request.data.get('datos_inscripcion') 
            fecha_str=datosMiembro['fecha']
            print(fecha_str)
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            # Serializar el miembro
            curp= datosMiembro['curp']
            
            password= curp[:10]
            print(password)
            serializerMiembro = MiembroSerializer(data=datosMiembro)
            #if not foto:
            #    return Response({"error": "No se ha proporcionado ninguna imagen."}, status= HTTP_400_BAD_REQUEST)
            if serializerMiembro.is_valid():
                
                miembro = serializerMiembro.save()
                num_control = miembro.num_control
                """
                path_on_supastorage = f"images/{miembro.num_control}.png"
                
                res = supabase.storage.from_('cadi_gym').upload(
                    path_on_supastorage,
                    file=foto.read(),
                    file_options={"content-type": foto.content_type}
                )
                
                miembro.foto = path_on_supastorage
                """
                miembro.save()
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
                    usuario = {
                        "correo": datosMiembro['correo'],
                        "password": password
                    }
                    return Response(data=usuario, status=HTTP_201_CREATED)
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

        except ExpiredSignatureError:
                # El token ha expirado
                return Response(data="El token ha expirado", status=HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
                # El token es inválido
                return Response(data="El token es inválido", status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)

class MiembrosActivos(APIView):
    def get(self, request):
        try:
            inscripciones = Inscripcion.objects.filter(acceso=True)
            
            miembros = [] 
            for inscripcion in inscripciones:  
                num_control = inscripcion.miembro.num_control  # Obtener el número de control del miembro
                datos_miembro = inscripcion.miembro

                # Buscar si el miembro ya está en la lista
                miembro_existente = next((miembro for miembro in miembros if miembro['num_control'] == num_control), None)

                if miembro_existente is None:
                    # Si el miembro no existe, crear un nuevo registro
                    lista_inscripciones = [{
                        'clase': inscripcion.clase,
                        'id': inscripcion.id
                    }]
                    historial_medico = HistorialMedico.objects.get(miembro=num_control) 
                    datos = {
                        'num_control': num_control,
                        'nombre': datos_miembro.nombre,
                        'paterno': datos_miembro.paterno,
                        'materno': datos_miembro.materno,
                        'edad': datos_miembro.edad,
                        'celular': datos_miembro.celular,
                        'alergias': historial_medico.alergias,
                        'inscripciones': lista_inscripciones
                    }
                    miembros.append(datos)  
                else:
                    # Si el miembro ya existe, agregar la inscripción a la lista de inscripciones
                    miembro_existente['inscripciones'].append({
                        'clase': inscripcion.clase,
                        'id': inscripcion.id
                    })
                    
            return Response(data=miembros, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)      

class VisitantesRegistrados(APIView):
    def put(self,request):
        try:
            correo=request.data.get('correo')
            clase=request.data.get('clase')
            costo=request.data.get('costo')
            visitante=Visitantes.objects.get(correo=correo, clase=clase)
            visitante.asistencias +=1
            print(visitante.asistencias)
            fecha_hoy = datetime.now().date()
            print(fecha_hoy)
            
            datos_pago={
                "estado":"pagado",
                "fecha_pago_realizado":fecha_hoy,
                "proximo_pago":fecha_hoy,
                "monto":costo,
                "visitante":visitante.id
            }
            
            serializer=PagosSerializer(data=datos_pago)
            if serializer.is_valid():
                visitante.save()
                serializer.save()
            else:
                print(serializer.errors)
                return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)
            
            return Response(data="Datos registrados", status=HTTP_200_OK)
        except Visitantes.DoesNotExist :
            return Response(data="No existen registros",status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)
""" 
class EditarMiembro(APIView):
    def put(self,request):
        try:
            
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)
 """

class DatosUsuario(APIView):
    def get(self,request):
        try:
            
            num_control=request.GET.get('user_id')
            historialDeportivo=HistorialDeportivo.objects.get(miembro=num_control)
            historialMedico=HistorialMedico.objects.get(miembro=num_control)
            miembro=Miembro.objects.get(num_control=num_control)
            serializerMiembro=MiembroSerializer(miembro)
            serializerDeportivo=HistorialDeportivoSerializer(historialDeportivo)
            serializerMedico=HistorialMedicoSerializer(historialMedico)
            datos={
                'datos_usuario':serializerMiembro.data,
                'historial_medico':serializerMedico.data,
                'historial_deportivo':serializerDeportivo.data
            } 
            return Response(data=datos,status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error", status=HTTP_400_BAD_REQUEST)
"""   
class x(APIView):
    def post(self, request):
        try:
            # Obtiene el archivo de la petición
            file = request.FILES.get('image')  # Asegúrate de que el campo se llame 'image'

            if not file:
                return Response({"error": "No se recibió ningún archivo."}, status=HTTP_400_BAD_REQUEST)

            # Define el nombre del blob (archivo en el bucket)
            blob_name = f'images/{2}'  # Puedes ajustar la ruta según sea necesario

            # Crea el blob y sube el archivo
            blob = bucket.blob(blob_name)
            blob.upload_from_file(file)

            # Obtiene la URL del archivo subido
            blob.make_public()
            image_url = blob.public_url
            print(image_url)
            return Response({"message": "Imagen subida exitosamente", "url": image_url}, status=HTTP_201_CREATED)

        except Exception as e:
            print(f"Error al subir la imagen: {e}")
            return Response({"error": "Ocurrió un error al subir la imagen"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
"""