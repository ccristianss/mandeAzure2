from firebase_config import db
from .models import *
from .serializers import *
from django.utils.timezone import now
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDay, TruncMonth
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import jwt, datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import uuid

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email_account')
        password = request.data.get('password_account')

        if not email or not password:
            return self.error_response('Missing email or password', status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(email_account=email)
        except Account.DoesNotExist:
            return self.error_response('Not Exist Account', status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Manejar otros errores de base de datos u excepciones
            return self.error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        if not check_password(password, account.password_account):
            return self.error_response('Invalid credentials', status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(account_id_account=account.id_account)
        except User.DoesNotExist:
            return self.error_response('Create User Profile', status.HTTP_401_UNAUTHORIZED)

        if not user.isactive_user:
            return self.error_response('Blocked account', status.HTTP_403_FORBIDDEN)

        token = self.generate_token(account)
        response = Response({'jwt': token, 'detail': 'Login successful'})
        response.set_cookie('jwt', token, httponly=True)
        return response

    def error_response(self, detail, status_code):
        response = Response({'detail': detail, 'jwt': ''}, status=status_code)
        response.delete_cookie('jwt')
        return response

    def generate_token(self, account):
        payload = {
            'id': account.id_account,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

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
        
        server_url = request.build_absolute_uri('/')[:-1]
        try:
            image_user = (server_url +  user.image_user.url )  if user.image_user else '' 
        except FileNotFoundError:
            image_user = ""

        token = generate_jwt(account)
        response = Response()

        if user.issuperadmin_user:
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token,
                'rol' : 'Superadmin',
                'name_user' : user.name_user,
                'lastname_user' : user.lastname_user,
                'image_user' : image_user,
                'detail': 'Inicio de sesión exitoso como Superadministrador'
            }
            response.status_code = status.HTTP_200_OK
            return response
        elif user.isadmin_user:
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token,
                'rol' : 'Admin',
                'name_user' : user.name_user,
                'lastname_user' : user.lastname_user,
                'image_user' : image_user,
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
        if not (user.isactive_user):
            raise AuthenticationFailed('Unauthenticated! Expired')
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

    # Obtener la fecha actual
    today = now().date()
    
    # Contadores de usuarios
    total_users = User.objects.filter(isadmin_user=False, issuperadmin_user=False).count()
    new_users_today = User.objects.filter(dateregister_user__date=today).count()
    new_users_by_month = User.objects.filter(dateregister_user__year=today.year).annotate(
        month=TruncMonth('dateregister_user')
    ).values('month').annotate(count=Count('id_user')).order_by('month')

    # Contadores de manders
    total_valid_manders = Mander.objects.filter(isvalidate_mander=True).count()
    active_valid_manders = Mander.objects.filter(isvalidate_mander=True, isactive_mander=True).count()
    manders_with_car = Mander.objects.filter(ishavecar_mander=True).count()
    manders_with_bike = Mander.objects.filter(ishavemoto_mander=True).count()

    # Contadores de requests
    total_requests = Request.objects.count()
    requests_by_service = Request.objects.values('service_id_service__name_service').annotate(count=Count('id_request'))
    priority_requests = Request.objects.filter(ispriority_request=True).count()
    requests_by_status = Request.objects.values('status_request').annotate(count=Count('id_request'))
    requests_today = Request.objects.filter(dateregister_request__date=today).count()

    # Filtrar requests por estado Proceso o Finalizado
    valid_request_ids = Request.objects.filter(
        Q(status_request='Proceso') | Q(status_request='Finalizado')
    ).values_list('id_request', flat=True)

    # Valor y cantidad de requests por día y por mes
    requests_and_value_by_day = RequestDetail.objects.filter(
        request_id_request__in=valid_request_ids,
        request_id_request__dateregister_request__year=today.year
    ).annotate(day=TruncDay('request_id_request__dateregister_request')).values('day').annotate(
        count=Count('id_requestdetail'), 
        total_value=Sum('price')
    ).order_by('day')

    requests_and_value_by_month = RequestDetail.objects.filter(
        request_id_request__in=valid_request_ids,
        request_id_request__dateregister_request__year=today.year
    ).annotate(month=TruncMonth('request_id_request__dateregister_request')).values('month').annotate(
        count=Count('id_requestdetail'), 
        total_value=Sum('price')
    ).order_by('month')

    total_requests_value = RequestDetail.objects.filter(
        request_id_request__in=valid_request_ids
    ).aggregate(total_value=Sum('price'))

    # Crear el diccionario de contadores
    count = {
        'users': {
            'total': total_users,
            'new_today': new_users_today,
            'new_by_month': list(new_users_by_month),
        },
        'manders': {
            'total_valid': total_valid_manders,
            'active_valid': active_valid_manders,
            'with_car': manders_with_car,
            'with_bike': manders_with_bike,
        },
        'requests': {
            'total': total_requests,
            'by_service': list(requests_by_service),
            'priority': priority_requests,
            'by_status': list(requests_by_status),
            'today': requests_today,
            'value_by_day': list(requests_and_value_by_day),
            'value_by_month': list(requests_and_value_by_month),
            'total_value': total_requests_value['total_value'],
        }
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
        queryset = User.objects.select_related('account_id_account').filter(
            isadmin_user=False,
            issuperadmin_user=False
        )
        serializer = ListUserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.select_related('account_id_account')
        user = queryset.filter(account_id_account=pk,
            isadmin_user=False,
            issuperadmin_user=False).first()
        if user:
            serializer = ListUserSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)

class ListManderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Mander.objects.select_related('user_id_user')
        idmander = request.query_params.get('idmander')
        if idmander:
            queryset = queryset.filter(id_mander=idmander)
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

class CreateUserAccountViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserAccountSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        iduser = self.request.query_params.get('iduser')
        if iduser:
            queryset = queryset.filter(id_user=iduser)
        return queryset

class VehicleManderUserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Vehicle.objects.select_related('user_id_user').filter(isactive_vehicle=True)
        serializer = VehicleManderUserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Vehicle.objects.select_related('user_id_user').filter(isactive_vehicle=True)
        mander = queryset.filter(user_id_user__mander__id_mander=pk).first()
        if mander:
            serializer = VehicleManderUserSerializer(mander, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"message": "User not found"}, status=404)
        
class RegisterAPIView(APIView):
    def post(self, request):
        email_account = request.data.get('email_account')
        
        if Account.objects.filter(email_account=email_account).exists():
            return Response({'detail': 'El correo electrónico ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el código de verificación
        verification_code = EmailVerification.objects.create(user=email_account)
        
        # Enviar el correo electrónico con el código de verificación
        subject = 'Código de Verificación de tu Registro'
        html_message = render_to_string('verification_email.html', {'verification_code': verification_code.code})
        plain_message = strip_tags(html_message)
        from_email = 'cristian.silva@crsi.dev'  # Reemplaza con tu dirección de correo
        to = email_account

        send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)
        
        return Response({'detail': 'Usuario registrado. Revisa tu correo para el código de verificación.'}, status=status.HTTP_201_CREATED)
    
class VerifyEmailAPIView(APIView):
    def post(self, request):
        email_account = request.data.get('email_account')
        code = request.data.get('code')
        
        try:
            verification_code = EmailVerification.objects.get(user=email_account, code=code)
        except (EmailVerification.DoesNotExist):
            return Response({'detail': 'Código de verificación inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        verification_code.delete()
        
        return Response({'detail': 'Correo electrónico verificado exitosamente.'}, status=status.HTTP_200_OK)

class ForgotPasswordAPIView(APIView):
    def post(self, request):
        email_account = request.data.get('email_account')

        try:
            account = Account.objects.get(email_account=email_account)
        except Account.DoesNotExist:
            return Response({'detail': 'El correo electrónico no está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar una nueva contraseña
        new_password = self.generate_random_password()

        # Asignar la nueva contraseña al usuario
        account.password_account = make_password(new_password)
        account.save()

        # Enviar la nueva contraseña por correo electrónico
        subject = 'Recuperación de Contraseña'
        html_message = render_to_string('password_reset_email.html', {'new_password': new_password})
        plain_message = strip_tags(html_message)
        from_email = 'cristian.silva@crsi.dev'  # Reemplaza con tu dirección de correo
        to = email_account

        send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=False)

        return Response({'detail': 'Se ha enviado una nueva contraseña a tu correo electrónico.'}, status=status.HTTP_200_OK)

    def generate_random_password(self):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10))  # Genera una contraseña de 10 caracteres
        return password