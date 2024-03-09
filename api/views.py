from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view


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



