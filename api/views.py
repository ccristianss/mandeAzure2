from firebase_config import db
from .models import *
from .serializers import *
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
import jwt, datetime
from django.conf import settings

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
        try:
            user = User.objects.get(account_id_account=account.id_account)
        except User.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        # Verificar si Account isactive_account
        if not user.isactive_user:
            return Response({'detail': 'Blocked account'}, status=status.HTTP_403_FORBIDDEN)
        # Si la autenticación es exitosa, devolver el ID de la cuenta
        payload = {
            'id': account.id_account,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        response.status_code = status.HTTP_200_OK

        return response

class AdminLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email_account')
        password = request.data.get('password_account')

        if not email or not password:
            return Response({'detail': 'Correo electrónico o contraseña faltante'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(email_account=email)
        except Account.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, account.password_account):
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(account_id_account=account.id_account)
        except User.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.isadmin_user:
            return Response({'detail': 'No tienes permisos de administrador'}, status=status.HTTP_403_FORBIDDEN)

        token = generate_custom_jwt(account, user)

        #try:
        #    user = User.objects.get(account_id_account=account.id_account)
        #except User.DoesNotExist:
        #    return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        # Devolver el token en la respuesta
        return Response({'token': token, 
                         'id_account': account.id_account,
                         #'name_user' : user.name_user,
                         #'lastname_user' : user.lastname_user,
                         'detail': 'Inicio de sesión exitoso como administrador'}, status=status.HTTP_200_OK)

def generate_custom_jwt(account, user):
    payload = {
        'id': account.id_account,
        'is_admin': user.isadmin_user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

class LoginFrontAPIView(APIView):
    def post(self, request):
        email = request.data.get('email_account')
        password = request.data.get('password_account')

        if not email or not password:
            return Response({'detail': 'Correo electrónico o contraseña faltante'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(email_account=email)
        except Account.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, account.password_account):
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(account_id_account=account.id_account)
        except User.DoesNotExist:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not (user.issuperadmin_user or user.isadmin_user):
            return Response({'detail': 'No tienes permisos Administrador'}, status=status.HTTP_403_FORBIDDEN)

        token = generate_jwt(account)
        response = Response()

        if user.issuperadmin_user:
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token,
                'rol' : 'Superadmin',
                'detail': 'Inicio de sesión exitoso como Superadministrador'
            }
            response.status_code = status.HTTP_200_OK
            return response
        elif user.isadmin_user:
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token,
                'rol' : 'Admin',
                'detail': 'Inicio de sesión exitoso como administrador'
            }
            response.status_code = status.HTTP_200_OK
            return response
        else:
            response.data = {
                'detail': 'Credenciales inválidas',
                'jwt': ''
                }
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.delete_cookie('jwt')
            return response


def generate_jwt(account):
    payload = {
        'id': account.id_account,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated! no token available')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
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
def contadores(request):
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

    # Crear el diccionario de contadores
    count = {
        'total_users': total_users,
        'total_manders': total_manders,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'processing_requests': processing_requests,
        'finished_requests': finished_requests,
        'active_manders': active_manders,
    }

    return Response(count)    
    
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        idaccount = self.request.query_params.get('idaccount')
        if idaccount:
            queryset = queryset.filter(account_id_account=idaccount)
        return queryset

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        iduser = self.request.query_params.get('iduser')
        if iduser:
            queryset = queryset.filter(user_id_user=iduser)
        return queryset

class ManderViewSet(viewsets.ModelViewSet):
    queryset = Mander.objects.all()
    serializer_class = ManderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        iduser = self.request.query_params.get('iduser')
        if iduser:
            queryset = queryset.filter(user_id_user=iduser)
        return queryset

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class RequestManagerViewSet(viewsets.ModelViewSet):
    queryset = Requestmanager.objects.all()
    serializer_class = RequestManagerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        id_request = self.request.query_params.get('idrequest')
        if id_request:
            queryset = queryset.filter(request_id_request=id_request)
        return queryset

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        iduser = self.request.query_params.get('iduser')
        if iduser:
            queryset = queryset.filter(user_id_user=iduser)
        return queryset

class RequestDetailViewset(viewsets.ModelViewSet):
    queryset = RequestDetail.objects.all()
    serializer_class = RequestDetailSerializer

class ListUserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.select_related('account_id_account')
        serializer = ListUserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.select_related('account_id_account')
        user = queryset.filter(account_id_account=pk).first()
        if user:
            serializer = ListUserSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)

class ListManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Mander.objects.select_related('user_id_user')
        serializer = ListManderSerializer(queryset, many=True, context={'request': self.request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Mander.objects.select_related('user_id_user')
        mander = queryset.filter(user_id_user=pk).first()
        if mander:
            serializer = ListManderSerializer(mander, context={'request': self.request})
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)

class ListRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Request.objects.prefetch_related('requestmanager')
    serializer_class = ListRequestSerializer

class ListAllRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Request.objects.all()
    serializer_class = ListAllRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related('service_id_service', 'user_id_user')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status_request=status)
        nostatus = self.request.query_params.get('nostatus')
        if nostatus:
            queryset = queryset.exclude(status_request=nostatus)
        iduser = self.request.query_params.get('iduser')
        if iduser:
            queryset = queryset.filter(user_id_user=iduser)
        idmander = self.request.query_params.get('idmander')
        if idmander:
            queryset = queryset.filter(requestmanager__mander_id_mander=idmander)
        return queryset

class PostRequestViewset(viewsets.ModelViewSet):
    queryset = RequestDetail.objects.all()
    serializer_class = PostRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(request_id_request__status_request=status)
        return queryset

class ListActiveManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Mander.objects.select_related('user_id_user').filter(
            user_id_user__isactive_user=True,
            isactive_mander=True,
            isvalidate_mander=True
        )
        serializer = ListActiveManderSerializer(queryset, many=True, context={'request': self.request})
        print(serializer.data)
        return Response(serializer.data)

class ListRequestManagerManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Requestmanager.objects.select_related('request_id_request')
        serializer = ListRequestManagerManderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        status = request.query_params.get('status')
        #print("Valor de 'status' recibido:", status) 
        try:
            requestmanager = Requestmanager.objects.select_related('request_id_request').filter(mander_id_mander=pk)
            serializer = ListRequestManagerManderSerializer(requestmanager, many=True)
            return Response(serializer.data)
        except Requestmanager.DoesNotExist:
            return Response({"message": "Requestmanager not found"}, status=404)

class GetRequestDetailAllViewSet(viewsets.ViewSet):
    serializer_class = PostRequestSerializer

    def list(self, request):
        queryset = RequestDetail.objects.all()
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(request_id_request__status_request=status)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        #queryset = RequestDetail.objects.all()
        id_request = RequestDetail.objects.filter(request_id_request=pk)
        if id_request:
            serializer = self.serializer_class(id_request, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)
        
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

class TokenViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):        
        ref = db.reference(f"/Manders/Tokens/{pk}/token")
        token = ref.get()
        
        if token:
            return Response({"token": token})
        else:
            return Response({"message": "Token not found for the user"}, status=404)

class ListAdminViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.select_related('account_id_account').filter(
            isadmin_user=True,
            issuperadmin_user=False
            )
        serializer = ListAdminSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.select_related('account_id_account')
        user = queryset.filter(
            account_id_account=pk,
            isadmin_user=True,
            issuperadmin_user=False
            ).first()
        if user:
            serializer = ListAdminSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)