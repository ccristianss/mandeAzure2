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
