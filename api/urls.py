from django.urls import path, include
from rest_framework import routers
from .models import *
from .views import *
from .import views

router = routers.DefaultRouter()
router.register(r'account', AccountViewSet)
router.register(r'user', UserViewSet)
router.register(r'document', DocumentViewSet)
router.register(r'mander', ManderViewSet)
router.register(r'service', ServiceViewSet)
router.register(r'request', RequestViewSet)
router.register(r'request_manager', RequestManagerViewSet)
router.register(r'vehicle', VehicleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/estadisticas/', estadisticas, name='estadisticas'),
]