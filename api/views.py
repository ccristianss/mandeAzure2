from .models import *
from .serializers import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView


# Create your views here.

@api_view(['GET'])
def estadisticas(request):
    # Calcular la cantidad total de cada modelo
    total_users = User.objects.count()
    total_manders = Mander.objects.count()
    total_requests = Request.objects.count()

    # Calcular la cantidad de solicitudes con diferentes estados
    pending_requests = Request.objects.filter(status_request='Pendiente').count()
    processing_requests = Request.objects.filter(status_request='Proceso').count()
    finished_requests = Request.objects.filter(status_request='Finalizado').count()

    # Calcular la cantidad de manders activos
    active_manders = Mander.objects.filter(isactive_mander=True).count()

    # Crear el diccionario de estadísticas
    statistics = {
        'total_users': total_users,
        'total_manders': total_manders,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'processing_requests': processing_requests,
        'finished_requests': finished_requests,
        'active_manders': active_manders,
    }

    return Response(statistics)    
    


class LoginAPIView(APIView):
    def post(self, request):
        # Obtener el correo electrónico y la contraseña del cuerpo de la solicitud
        email = request.data.get('email_account')
        password = request.data.get('password_account')
        if not email or not password:
            return Response({'detail': 'Missing email or password'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar un usuario con el mismo correo electrónico
        try:
            account = Account.objects.get(email_account=email)
        except Account.DoesNotExist:
            # Si el usuario no existe, puedes devolver un error
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Manejar otros errores de base de datos u excepciones
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Verificar si la contraseña coincide
        if not check_password(password, account.password_account):
            # Si la contraseña es correcta, devolver el id_account
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        # Si la autenticación es exitosa, devolver el ID de la cuenta
        return Response({'id_account': account.id_account}, status=status.HTTP_200_OK)

    
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  
    serializer_class = UserSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class ManderViewSet(viewsets.ModelViewSet):
    queryset = Mander.objects.all()
    serializer_class = ManderSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class RequestManagerViewSet(viewsets.ModelViewSet):
    queryset = Requestmanager.objects.all()
    serializer_class = RequestmanagerSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer



