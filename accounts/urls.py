from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('register/status/<str:username>/', views.registration_status, name='registration_status'),
    path('admin_verify/', views.admin_verify, name='admin_verify'),
]