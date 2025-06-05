from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'patients', views.PatientViewSet, basename='patient')
router.register(r'services', views.ServiceViewSet, basename='service')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/user/', views.get_current_user, name='get_current_user'),
    path('dashboard/', views.get_dashboard_data, name='dashboard'),
    path('bills/', views.CreateBillView.as_view(), name='bill-create'),
    path('bills/list/', views.BillViewSet.as_view({'get': 'list'}), name='bill-list'),
    path('bills/<int:pk>/', views.BillViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='bill-detail'),
    path('bills/daily-report/', views.BillViewSet.as_view({'get': 'daily_report'}), name='bill-daily-report'),
    path('patients/<int:pk>/add_medical_record/', views.PatientViewSet.as_view({'post': 'add_medical_record'}), name='add-medical-record'),
    path('patients/<int:pk>/add_medical_report/', views.PatientViewSet.as_view({'post': 'add_medical_report'}), name='add-medical-report'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]