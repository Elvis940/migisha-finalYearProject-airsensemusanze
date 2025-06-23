# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('user/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('user/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('user/register/', views.register_user, name='register_user'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('api/sensordata/latest/', views.latest_sensor_data, name='latest_sensor_data'),
    path('api/sensordata/', views.receive_sensor_data, name='receive_sensor_data'),
     path('api/sensordata/historical/', views.historical_sensor_data, name='historical_sensor_data'),
     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard')

]
