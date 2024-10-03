from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_404_NOT_FOUND
from .models import Pagos
from miembros.models import Miembro
from inscripciones.models import Inscripcion 
from .serializers import PagosSerializer,PagosPendientes
from inscripciones.serializers import InscripcionSerializer
from datetime import date,datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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
                pago_info = {
                    "id": pago.id,
                    "estado": pago.estado,
                    "fecha_pago_realizado": pago.fecha_pago_realizado,
                    "proximo_pago": pago.proximo_pago,
                    "monto": str(pago.monto),  # Asegúrate de que el monto sea un string
                    "miembro": pago.miembro.num_control,  # Asumiendo que 'miembro' es una relación
                    "inscripcion": inscripcion.id,
                    "clase": inscripcion.clase,  # Asegúrate de que 'clase' está disponible en el objeto 'inscripcion'
                    "modalidad": inscripcion.modalidad,  # Asegúrate de que 'modalidad' está disponible en el objeto 'inscripcion'
                }
                # Verifica la modalidad y la fecha del próximo pago
                if inscripcion.modalidad == 'Mes' and pago.proximo_pago >= fecha_actual:
                    pago_info["monto"] = "500.00"
                    
                elif inscripcion.modalidad == 'Mes (de 5 a 6 años)' and pago.proximo_pago >= fecha_actual:
                    print("inscripcion niño")
                    pago_info["monto"] = "680.00"
                    
                elif inscripcion.modalidad == 'Mes (7 años en adelante)' and pago.proximo_pago >= fecha_actual:
                    print("inscripcion adulto")
                    pago_info["monto"] = "760.00"
                    
                elif pago.proximo_pago < fecha_actual:
                    pago_info["monto"] = str(float(pago.monto) + 50)  # Actualiza el monto
                else:
                    pago_info["monto"] = str(pago.monto)  # Monto original si no se aplica ninguna condición

                # Agrega el diccionario a la lista de pagos válidos
                pagos_validos.append(pago_info)

            # Serializa solo los pagos válidos 
            return Response(data=pagos_validos)

        except Miembro.DoesNotExist as e:
            print(e)
            return Response({"error": "Usuario no encontrado"}, status=404)
        except Exception as e:
            print(e)
            return Response({"error": "Ocurrió un error en la solicitud"}, status=500)

class RegistrarPago(APIView):
    def post(self,request):
        try:
            fecha_pago= request.data.get('fecha_pago')
            monto = request.data.get('monto')
            id_pago = request.data.get('id_pago')
            pago = Pagos.objects.get(id=id_pago)
            pago.fecha_pago_realizado=fecha_pago
            pago.estado='pagado'
            miembro= pago.miembro
            fecha=pago.proximo_pago
            
            inscripcion=pago.inscripcion
            datos_inscripcion= Inscripcion.objects.get(id= inscripcion.id)
            modalidad = datos_inscripcion.modalidad
            datos_inscripcion.acceso=True
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
            print(proximo_pago)
            nuevo_pago={
                'fecha_pago_realizado': None,  # No se ha realizado el pago
                'estado': 'pendiente',
                'inscripcion': inscripcion.id,
                'miembro':  miembro.num_control,
                'monto': monto,  # Puede ser el mismo monto
                'proximo_pago': proximo_pago # Usar la misma fecha
            }
            
            serializer= PagosSerializer(data=nuevo_pago)
            
            if serializer.is_valid():
                pago.save()
                datos_inscripcion.save()
                serializer.save()
            else:
                return Response(data="Datos de pago incorrectos",status=HTTP_404_NOT_FOUND)
            return Response(data="Pago registrado",status=HTTP_200_OK)
        except Pagos.DoesNotExist as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_404_NOT_FOUND)
        except Inscripcion.DoesNotExist as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response(data="Ocurrio un error",status=HTTP_400_BAD_REQUEST)

class PagosPendientes(APIView):
    def get(self,request):
        try:
            # Obtener la fecha actual
            hoy = timezone.now()
            mes_actual = hoy.month  # Mes actual
            anio_actual = hoy.year  # Año actual

            # Filtrar pagos pendientes donde el mes de pago_proximo sea igual al mes actual
            pagos = Pagos.objects.filter(
                estado='pendiente',
                proximo_pago__month=mes_actual,
                proximo_pago__year=anio_actual# Filtrar por mes
            )

            # Si necesitas devolver los datos en un formato específico
            datos_pagos = []  # Crear una lista para almacenar los datos a devolver
            for pago in pagos:
                datos_pagos.append({
                    'id': pago.id,
                    'monto': pago.monto,
                    'pago_proximo': pago.proximo_pago,
                    'estado': pago.estado,
                    # Agrega otros campos según necesites
                })

            return Response(data=datos_pagos, status=HTTP_200_OK)

        except Exception as e:
            print(f"Ocurrió un error: {e}")  # Para propósitos de depuración
            return Response(data="Ocurrió un error", status=HTTP_400_BAD_REQUEST)