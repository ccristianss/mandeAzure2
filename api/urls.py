from django.urls import path, include
from rest_framework import routers
from .models import *
from .views import *

router = routers.DefaultRouter()
router.register(r'account', AccountViewSet)
router.register(r'user', UserViewSet, basename='user')
router.register(r'document', DocumentViewSet)
router.register(r'mander', ManderViewSet)
router.register(r'service', ServiceViewSet)
router.register(r'request', RequestViewSet)
router.register(r'request_manager', RequestManagerViewSet)
router.register(r'vehicle', VehicleViewSet)
router.register(r'getlistuser', GetListUserViewSet, basename='getlistuser')
router.register(r'listrequestmanagermander', ListRequestManagerManderViewSet, basename='listrequestmanagermander')
router.register(r'requestdetails', RequestDetailViewset, basename='requestdetails')
router.register(r'allrequests', RequestAllViewset, basename='allrequests')
router.register(r'getlistmanders', GetListManderViewSet, basename='getlistmanders')
router.register(r'request_list',RequestListViewSet, basename='request_list')
router.register(r'manderdetail', ManderDetailViewSet, basename='manderdetail')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api2/login/', LoginAPIView.as_view(), name='login'),
    path('api2/user_data/', UserView.as_view(), name='user_data'),
    path('api2/logout/', LogoutView.as_view(), name='logout'),
    path('api/estadisticas/', estadisticas, name='estadisticas'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]