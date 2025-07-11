from django.db import models
from django.contrib.auth.hashers import make_password
import random
import string

class Account(models.Model):
    id_account           = models.AutoField(primary_key=True)
    email_account        = models.EmailField(max_length=254, unique=True)
    password_account     = models.CharField(max_length=255)
    dateregister_account = models.DateTimeField(auto_now_add=True)
    dateupdate_account   = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        if not self.password_account.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password_account = make_password(self.password_account)
        super().save(*args, **kwargs)
   
    def __str__(self):
        return self.email_account
    
    def get_id(self):
        return self.id_account
    class Meta:
        db_table = 'account'
    
class User(models.Model):
    id_user            = models.AutoField(primary_key=True)
    account_id_account = models.OneToOneField(Account, on_delete=models.PROTECT, unique=True)
    image_user         = models.ImageField(upload_to='imgProfiles', null=True, blank=True)
    name_user          = models.CharField(max_length=45)
    lastname_user      = models.CharField(max_length=45)
    phone_user         = models.CharField(max_length=10)
    dateregister_user  = models.DateTimeField(auto_now_add=True)
    dateupdate_user    = models.DateTimeField(auto_now=True)
    ismander_user      = models.BooleanField(default=False)
    isadmin_user       = models.BooleanField(default=False)
    isactive_user      = models.BooleanField(default=True)
    issuperadmin_user  = models.BooleanField(default=False)

    def __str__(self):
        return self.name_user
    class Meta:
        db_table = 'user'

class Document(models.Model):
    id_document         = models.AutoField(primary_key=True)
    user_id_user        = models.ForeignKey(User, on_delete=models.PROTECT)
    image_document      = models.ImageField(upload_to='imgDocs', null=True, blank=True)
    isdocument_vehicle  = models.BooleanField(default=True)
    isverified_document = models.BooleanField(default=False)

    DOCUMENT_TYPES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('SOAT', 'SOAT'),
        ('LICENCIA', 'Licencia'),
        ('OPERACION', 'Operación'),
        ('TECNOMECANICA', 'Tecnomecánica'),
        ('RECIBO', 'Recibo'),
    ]

    type_document = models.CharField(max_length=15, choices=DOCUMENT_TYPES)

    dateregister_document = models.DateTimeField(auto_now_add=True)
    dateupdate_document   = models.DateTimeField(auto_now=True)
    dateverified_document = models.DateTimeField(null=True)

    def __str__(self):
        return self.type_document
    class Meta:
        db_table = 'document'

class Mander(models.Model):
    id_mander           = models.AutoField(primary_key=True)
    user_id_user        = models.OneToOneField(User, on_delete=models.PROTECT, unique=True)
    image_mander        = models.ImageField (upload_to='imgMander', null=True, blank=True)
    ishavecar_mander    = models.BooleanField(default=False)
    ishavemoto_mander   = models.BooleanField(default=False)
    isactive_mander     = models.BooleanField(default=False)
    isvalidate_mander   = models.BooleanField(default=False)
    dateregister_mander = models.DateTimeField(auto_now_add=True)
    dateupdate_mander   = models.DateTimeField(auto_now=True)
    address_mander      = models.CharField(max_length=100)
    cc_mander           = models.CharField(max_length=13, unique=True)
    def __str__(self):
        return self.cc_mander
    class Meta:
        db_table = 'mander'

class Service(models.Model):
    id_service          = models.AutoField(primary_key=True)
    name_service        = models.CharField(max_length=45)
    detail_service      = models.CharField(max_length=255)
    image_service       = models.ImageField(upload_to='imgService', null=True, blank=True)
    isvisible_service   = models.BooleanField(default=False)

    def __str__(self):
        return self.name_service
    
    class Meta:
        db_table = 'service'

class Request(models.Model):
    id_request         = models.AutoField(primary_key=True)
    service_id_service = models.ForeignKey(Service, on_delete=models.PROTECT)
    user_id_user       = models.ForeignKey(User, on_delete=models.PROTECT)
    detail_request     = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Proceso', 'Proceso'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]

    status_request       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')

    VEHICLE_TYPE_CHOICES = [
        ('none', 'None'),
        ('bicycle', 'Bicycle'),
        ('bike', 'Motorcycle'),
        ('car', 'Car'),
    ]
    typevehicle_request     = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, default='none')
    ispriority_request      = models.BooleanField(default=False)
    dateregister_request    = models.DateTimeField(auto_now_add=True)
    dateupdate_request      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Request {self.id_request}: {self.detail_request}'
    
    class Meta:
        db_table = 'request'

class Requestmanager(models.Model):
    id_requestmanager    = models.AutoField(primary_key=True)
    request_id_request   = models.OneToOneField(Request, on_delete=models.PROTECT, unique=True)
    image_requestmanager = models.ImageField(upload_to='imgRequestmanager', null=True, blank=True)
    imageprocess_requestmanager = models.ImageField(upload_to='imgRequestmanager', null=True, blank=True)
    mander_id_mander     = models.ForeignKey(Mander, on_delete=models.PROTECT)

    STATUS_CHOICES = [
        ('espera', 'En espera'),
        ('proceso', 'En proceso'),
        ('terminado', 'Terminado'),
    ]
    status_requestmanager       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='espera')
    detail_requestmanager       = models.CharField(max_length=255)
    dateregister_requestmanager = models.DateTimeField(auto_now_add=True)
    dateupdate_requestmanager   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.detail_requestmanager
    class Meta:
        db_table = 'requestmanager'

class Vehicle(models.Model):
    id_vehicle          = models.AutoField(primary_key=True)
    user_id_user        = models.ForeignKey(User, on_delete=models.PROTECT)
    image_vehicle       = models.ImageField(upload_to='imgVehicles', null=True, blank=True)
    brand_vehicle       = models.CharField(max_length=20)
    plate_vehicle       = models.CharField(max_length=10, unique=True)
    model_vehicle       = models.CharField(max_length=4)
    color_vehicle       = models.CharField(max_length=45)

    VEHICLE_TYPE_CHOICES = [
        ('none', 'None'),
        ('bicycle', 'Bicycle'),
        ('bike', 'Motorcycle'),
        ('car', 'Car'),
    ]
    type_vehicle         = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    isverified_vehicle   = models.BooleanField(default=False)
    isactive_vehicle     = models.BooleanField(default=False)
    dateregister_vehicle = models.DateTimeField(auto_now_add=True)
    dateupdate_vehicle   = models.DateTimeField(auto_now=True)
    dateverified_vehicle = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plate_vehicle
    class Meta:
        db_table = 'vehicle'

class RequestDetail(models.Model):
    id_requestdetail    = models.AutoField(primary_key=True)
    request_id_request  = models.OneToOneField(Request, on_delete=models.PROTECT, unique=True)
    origin              = models.CharField(max_length=255, null=True)
    originLat           = models.FloatField(default=0.0)
    originLng           = models.FloatField(default=0.0)
    destination         = models.CharField(max_length=255, null=True)
    destinationLat      = models.FloatField(default=0.0)
    destinationLng      = models.FloatField(default=0.0)
    current             = models.CharField(max_length=255, null=True)
    currentLat          = models.FloatField(default=0.0)
    currentLng          = models.FloatField(default=0.0)
    distance            = models.IntegerField(default=0)
    time                = models.IntegerField(default=0) 
    points              = models.TextField(null=True)
    price               = models.FloatField(default=0.0)

    def __str__(self):
        return self.id_requestdetail
    class Meta:
        db_table = 'requestdetail'

class EmailVerification(models.Model):
    user = models.EmailField(null=False)
    code = models.CharField(max_length=8, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(8))
    class Meta:
        db_table = 'emailverification'