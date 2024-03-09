from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    account_id_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), allow_null=True)
    
    class Meta:
        model = User
        fields = '__all__'
        depth=2

        
        
    

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
