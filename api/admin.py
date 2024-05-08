from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Account)
admin.site.register(User)
admin.site.register(Document)
admin.site.register(Mander)
admin.site.register(Service)
admin.site.register(Request)
admin.site.register(Requestmanager)
admin.site.register(RequestDetail)
admin.site.register(Vehicle)