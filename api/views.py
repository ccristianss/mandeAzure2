from .models import *
from .serializers import *
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
import jwt, datetime

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
        payload = {
            'id': account.id_account,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'manders', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        response.status_code = status.HTTP_200_OK

        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        #print("Token:", token) 
        #token2 = request.headers.get('Authorization')
        #_, token2 = token2.split()
        #print("Token2:", token2) 
        if not token:
            raise AuthenticationFailed('Unauthenticated! no token available')
        try:
            payload = jwt.decode(token, 'manders', algorithms=['HS256'])
            #expiration_timestamp = payload['exp']
            #expiration_date = datetime.datetime.utcfromtimestamp(expiration_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            #print("Expiration:", expiration_date)
            #timestamp = payload['iat']
            #datenow = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            #print("datenow:", datenow)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated! Expired')

        user = User.objects.filter(account_id_account=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success',
            'jwt': ''
        }
        return response

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

class GetListUserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.select_related('account_id_account')
        serializer = ListUserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.select_related('account_id_account')
        user = queryset.filter(account_id_account=pk).first()
        if user:
            serializer = ListUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)

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

class ListRequestManagerManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Requestmanager.objects.select_related('request_id_request')
        serializer = ListRequestManagerManderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        status = request.query_params.get('status')
        print("Valor de 'status' recibido:", status) 
        try:
            requestmanager = Requestmanager.objects.select_related('request_id_request').filter(mander_id_mander=pk)
            serializer = ListRequestManagerManderSerializer(requestmanager, many=True)
            return Response(serializer.data)
        except Requestmanager.DoesNotExist:
            return Response({"message": "Requestmanager not found"}, status=404)

class RequestDetailViewset(viewsets.ModelViewSet):
    queryset = RequestDetail.objects.all()
    serializer_class = RequestDetailSerializer

class RequestAllViewset(viewsets.ModelViewSet):
    queryset = RequestDetail.objects.all()
    serializer_class = RequestAllSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(request_id_request__status_request=status)
        return queryset

class GetListManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Mander.objects.select_related('user_id_user')
        serializer = CustomManderSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Mander.objects.select_related('user_id_user')
        mander = queryset.filter(user_id_user=pk).first()
        if mander:
            serializer = CustomManderSerializer(mander)
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)

class RequestListView(generics.ListAPIView):
    serializer_class = RequestListSerializer

    def get_queryset(self):
        queryset = Request.objects.prefetch_related('requestmanager')
        return queryset

class RequestListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Request.objects.prefetch_related('requestmanager')
    serializer_class = RequestListSerializer

class ManderDetailViewSetxx(viewsets.ViewSet): 
    def list(self, request):
        queryset = Mander.objects.select_related('user_id_user')
        serializer = ManderDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            mander = Mander.objects.select_related('user_id_user').get(pk=pk)
            serializer = ManderDetailSerializer(mander)
            return Response(serializer.data)
        except Mander.DoesNotExist:
            return Response({"message": "Mander not found"}, status=404)
        
class ManderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mander.objects.select_related('user_id_user__account_id_account').prefetch_related('user_id_user__vehicle_set')
    serializer_class = ManderDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            mander = self.get_object()
            serializer = self.get_serializer(mander)
            return Response(serializer.data)
        except Mander.DoesNotExist:
            return Response({"message": "Mander not found"}, status=404)