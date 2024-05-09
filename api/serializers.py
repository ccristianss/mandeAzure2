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

class RequestManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requestmanager
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDetail
        fields = '__all__'

class ListUserSerializer(serializers.ModelSerializer):
    id_account = serializers.PrimaryKeyRelatedField(source='account_id_account', read_only=True)
    email_account = serializers.CharField(source='account_id_account.email_account', read_only=True)
    def get_image_user(self, obj):
        request = self.context.get('request')        
        if request is not None and obj.image_user:
            server_url = request.build_absolute_uri('/')[:-1]
            image_url = obj.image_user.url
            full_url = server_url + image_url
            return full_url
        return None
    
    class Meta:
        model = User
        fields = ['id_user', 'id_account', 'email_account', 'isactive_user', 'isadmin_user', 'image_user', 
                  'name_user', 'lastname_user', 'phone_user', 'ismander_user']

class ListManderSerializer(serializers.ModelSerializer):
    id_account = serializers.PrimaryKeyRelatedField(source='user_id_user.account_id_account', read_only=True)
    email_account = serializers.CharField(source='user_id_user.account_id_account.email_account', read_only=True)
    isactive_user = serializers.BooleanField(source='user_id_user.isactive_user', read_only=True)
    id_user = serializers.PrimaryKeyRelatedField(source='user_id_user.id_user', read_only=True)
    name_user = serializers.CharField(source='user_id_user.name_user', read_only=True)
    lastname_user = serializers.CharField(source='user_id_user.lastname_user', read_only=True)
    phone_user = serializers.CharField(source='user_id_user.phone_user', read_only=True)
    ismander_user = serializers.BooleanField(source='user_id_user.ismander_user', read_only=True)
    documents = DocumentSerializer(many=True, source='user_id_user.document_set', read_only=True)
    vehicles = VehicleSerializer(many=True, source='user_id_user.vehicle_set', read_only=True)

    def get_image_mander(self, obj):
        request = self.context.get('request')        
        if request is not None and obj.image_mander:
            server_url = request.build_absolute_uri('/')[:-1]
            image_url = obj.image_mander.url
            full_url = server_url + image_url
            return full_url
        return None

    class Meta:
        model = Mander
        fields = ['id_mander', 'id_user', 'id_account', 'email_account', 'isactive_user',
                  'name_user', 'lastname_user', 'phone_user', 'ismander_user','image_mander',
                  'ishavecar_mander', 'ishavemoto_mander', 'isactive_mander', 'isvalidate_mander',
                  'address_mander', 'cc_mander', 'documents', 'vehicles']

class ListRequestSerializer(serializers.ModelSerializer):
    id_mander = serializers.PrimaryKeyRelatedField(source='requestmanager.mander_id_mander',read_only=True)
    name_mander = serializers.CharField(source='requestmanager.mander_id_mander.user_id_user.name_user',read_only=True)
    lastname_mander = serializers.CharField(source='requestmanager.mander_id_mander.user_id_user.lastname_user',read_only=True)
    name_user = serializers.CharField(source='user_id_user.name_user',read_only=True)
    lastname_user = serializers.CharField(source='user_id_user.lastname_user',read_only=True)
    phone_user = serializers.CharField(source='user_id_user.phone_user',read_only=True)
    id_requestmanager = serializers.PrimaryKeyRelatedField(source='requestmanager',read_only=True)
    origin = serializers.CharField(source='requestdetail.origin',read_only=True)
    originLat = serializers.CharField(source='requestdetail.originLat',read_only=True)
    originLng = serializers.CharField(source='requestdetail.originLng',read_only=True)
    destination = serializers.CharField(source='requestdetail.destination',read_only=True)
    destinationLat = serializers.CharField(source='requestdetail.destinationLat',read_only=True)
    destinationLng =serializers.CharField(source='requestdetail.destinationLng',read_only=True)

    class Meta:
        model = Request
        fields = ['name_user', 'lastname_user', 'phone_user', 'name_mander', 'lastname_mander','id_mander','id_requestmanager','id_request',
                  'user_id_user','detail_request','status_request', 'origin', 'originLat', 'originLng', 
                  'destination', 'destinationLat', 'destinationLng', 'typevehicle_request', 'ispriority_request', 'dateregister_request', 'dateupdate_request']

class ListAllRequestSerializer(serializers.ModelSerializer):
    requestmanager = RequestManagerSerializer(read_only=True)
    requestdetail = RequestDetailSerializer()

    def get_requestmanager(self, obj):
        try:
            request_manager = Requestmanager.objects.get(request_id_request=obj)
            return RequestManagerSerializer(request_manager).data
        except Requestmanager.DoesNotExist:
            return None

    def get_requestdetail(self, obj):
        try:
            request_detail = RequestDetail.objects.get(request_id_request=obj)
            return RequestDetailSerializer(request_detail).data
        except RequestDetail.DoesNotExist:
            return None

    class Meta:
        model = Request
        fields = '__all__'

class PostRequestSerializer(serializers.ModelSerializer):
    request_id_request = RequestSerializer()
    class Meta:
        model = RequestDetail
        fields = '__all__'

    def create(self, validated_data):
        request_data = validated_data.pop('request_id_request')
        request_instance = Request.objects.create(**request_data)
        request_detail_instance = RequestDetail.objects.create(request_id_request=request_instance, **validated_data)
        return request_detail_instance

    def update(self, instance, validated_data):
            request_data = validated_data.pop('request_id_request', None)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if request_data:
                request_instance = instance.request_id_request
                for attr, value in request_data.items():
                    setattr(request_instance, attr, value)
                request_instance.save()

            return instance

class ListActiveManderSerializer(serializers.ModelSerializer):
    email_account = serializers.CharField(source='user_id_user.account_id_account.email_account', read_only=True)
    name_user = serializers.CharField(source='user_id_user.name_user', read_only=True)
    lastname_user = serializers.CharField(source='user_id_user.lastname_user', read_only=True)
    phone_user = serializers.CharField(source='user_id_user.phone_user', read_only=True)

    class Meta:
        model = Mander
        fields = ['id_mander', 'email_account', 'name_user', 'lastname_user', 'phone_user']

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

class ManderDetailSerializer(serializers.ModelSerializer):
    id_user = serializers.PrimaryKeyRelatedField(source='user_id_user', read_only=True)
    name_user = serializers.CharField(source='user_id_user.name_user', read_only=True)
    id_account = serializers.PrimaryKeyRelatedField(source='user_id_user.account_id_account', read_only=True)
    email_account = serializers.CharField(source='user_id_user.account_id_account.email_account', read_only=True)
    ismander_user = serializers.BooleanField(source='user_id_user.ismander_user', read_only=True)
    id_vehicle = serializers.PrimaryKeyRelatedField(source='user_id_user.vehicle_set.first', read_only=True)
    brand_vehicle = serializers.SerializerMethodField()
    model_vehicle = serializers.SerializerMethodField()
    color_vehicle = serializers.SerializerMethodField()
    id_document = serializers.SerializerMethodField()
    type_document = serializers.SerializerMethodField()

    def get_brand_vehicle(self, obj):
        if obj.user_id_user.vehicle_set.exists():
            return obj.user_id_user.vehicle_set.first().brand_vehicle
        return None

    def get_model_vehicle(self, obj):
        if obj.user_id_user.vehicle_set.exists():
            return obj.user_id_user.vehicle_set.first().model_vehicle
        return None

    def get_color_vehicle(self, obj):
        if obj.user_id_user.vehicle_set.exists():
            return obj.user_id_user.vehicle_set.first().color_vehicle
        return None
    
    def get_id_document(self, obj):
        if obj.user_id_user.document_set.exists():
            return obj.user_id_user.document_set.first().id_document
        return None

    def get_type_document(self, obj):
        if obj.user_id_user.document_set.exists():
            return obj.user_id_user.document_set.first().type_document
        return None
    
    class Meta:
        model = Mander
        fields = ['id_user', 'name_user', 'id_account', 'email_account', 'ismander_user', 'id_vehicle', 'brand_vehicle', 'model_vehicle', 'color_vehicle', 'id_document', 'type_document']



class ListAdminSerializer(serializers.ModelSerializer):
    id_account = serializers.PrimaryKeyRelatedField(source='account_id_account', read_only=True)
    email_account = serializers.CharField(source='account_id_account.email_account', read_only=True)
    def get_image_user(self, obj):
        request = self.context.get('request')        
        if request is not None and obj.image_user:
            server_url = request.build_absolute_uri('/')[:-1]
            image_url = obj.image_user.url
            full_url = server_url + image_url
            return full_url
        return None
    
    class Meta:
        model = User
        fields = ['id_user', 'id_account', 'email_account', 'isactive_user', 'isadmin_user', 'image_user', 
                  'name_user', 'lastname_user', 'phone_user', 'ismander_user']
