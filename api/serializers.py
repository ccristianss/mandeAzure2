from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ListUserSerializer(serializers.ModelSerializer):
    id_account = serializers.PrimaryKeyRelatedField(source='account_id_account', read_only=True)
    email_account = serializers.CharField(source='account_id_account.email_account', read_only=True)
    isadmin_account = serializers.BooleanField(source='account_id_account.isadmin_account', read_only=True)
    class Meta:
        model = User
        fields = ['id_user', 'id_account', 'email_account', 'isadmin_account', 'image_user', 'name_user', 'lastname_user', 'phone_user', 'ismander_user']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class ManderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mander
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

class RequestmanagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requestmanager
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class ListRequestManagerManderSerializer(serializers.ModelSerializer):
    id_request = serializers.PrimaryKeyRelatedField(source='request_id_request', read_only=True)
    detail_request = serializers.CharField(source='request_id_request.detail_request', read_only=True)
    status_request = serializers.CharField(source='request_id_request.status_request', read_only=True)
    name_user = serializers.CharField(source='request_id_request.user_id_user', read_only=True)
    id_user = serializers.PrimaryKeyRelatedField(source='request_id_request.user_id_user.id_user', read_only=True)
    name_mander = serializers.CharField(source='mander_id_mander.user_id_user', read_only=True)
    name_service = serializers.CharField(source='request_id_request.service_id_service', read_only=True)
    id_service = serializers.PrimaryKeyRelatedField(source='request_id_request.service_id_service.id_service', read_only=True)
    class Meta:
        model = Requestmanager
        fields = ['id_requestmanager', 'status_requestmanager', 'detail_requestmanager', 'id_request', 'status_request', 'detail_request', 'id_service', 'name_service', 'id_user', 'name_user', 'mander_id_mander', 'name_mander']
        
class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDetail
        fields = '__all__'

class RequestAllSerializer(serializers.ModelSerializer):
    request_id_request = RequestSerializer()
    class Meta:
        model = RequestDetail
        fields = '__all__'

    def create(self, validated_data):
        request_data = validated_data.pop('request_id_request')
        request_instance = Request.objects.create(**request_data)
        request_detail_instance = RequestDetail.objects.create(request_id_request=request_instance, **validated_data)
        return request_detail_instance

class CustomManderSerializer(serializers.ModelSerializer):
    id_account = serializers.PrimaryKeyRelatedField(source='user_id_user.account_id_account', read_only=True)
    email_account = serializers.CharField(source='user_id_user.email_account', read_only=True)
    password_account = serializers.CharField(source='user_id_user.password_account', read_only=True)
    isadmin_account = serializers.BooleanField(source='user_id_user.isadmin_account', read_only=True)
    id_user = serializers.PrimaryKeyRelatedField(source='user_id_user.id_user', read_only=True)
    image_id_image = serializers.PrimaryKeyRelatedField(source='user_id_user.image_id_image', read_only=True)
    name_user = serializers.CharField(source='user_id_user.name_user', read_only=True)
    lastname_user = serializers.CharField(source='user_id_user.lastname_user', read_only=True)
    phone_user = serializers.CharField(source='user_id_user.phone_user', read_only=True)
    ismander_user = serializers.BooleanField(source='user_id_user.ismander_user', read_only=True)

    class Meta:
        model = Mander
        fields = ['id_mander', 'id_user', 'id_account', 'email_account', 'password_account', 'isadmin_account',
                  'name_user', 'lastname_user', 'phone_user', 'ismander_user', 'image_id_image',
                  'ishavecar_mander', 'ishavemoto_mander', 'isactive_mander', 'isvalidate_mander',
                  'address_mander', 'cc_mander']