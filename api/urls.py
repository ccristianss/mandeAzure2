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
router.register(r'request_detail', RequestDetailViewset, basename='request_detail')
router.register(r'getlistuser', ListUserViewSet, basename='getlistuser')
router.register(r'getlistadmin', ListAdminViewSet, basename='getlistadmin')
router.register(r'getlistmanders', ListManderViewSet, basename='getlistmanders')
router.register(r'getlistrequest', ListRequestViewSet, basename='getlistrequest')
router.register(r'listallrequest', ListAllRequestViewSet, basename='listallrequest')
router.register(r'postrequest', PostRequestViewset, basename='postrequest')
router.register(r'getlistactivemanders', ListActiveManderViewSet, basename='getlistactivemanders')
router.register(r'postuseraccount', CreateUserAccountViewset, basename='postuseraccount')
router.register(r'getvehiclemander', VehicleManderUserViewSet, basename='getvehiclemander')

# Eliminar Routes 
router.register(r'listrequestmanagermander', ListRequestManagerManderViewSet, basename='listrequestmanagermander')
router.register(r'getallrequestsdetail', GetRequestDetailAllViewSet, basename='getallrequests')
router.register(r'manderdetail', ManderDetailViewSet, basename='manderdetail')
router.register(r'tokens', TokenViewSet, basename='tokens')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api2/login/', LoginAPIView.as_view(), name='login'),
    path('api2/admin/login/', AdminLoginAPIView.as_view(), name='admin_login'),
    path('api2/login2/', LoginFrontAPIView.as_view(), name='login2'),
    path('api2/user_data/', UserView.as_view(), name='user_data'),
    path('api2/logout/', LogoutView.as_view(), name='logout'),
    path('api/contadores/', contadores, name='contadores'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api2/register/', RegisterAPIView.as_view(), name='register'),
    path('api2/verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('api2/forgotpassword/', ForgotPasswordAPIView.as_view(), name='forgotpassword'),
]