"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import normal_register, verify_otp, logout_view 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('profile/', views.edit_profile, name='edit_profile'),
    path('login/', views.normal_login, name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('normal_register/', normal_register, name='register'),
    path('varify_otp/', verify_otp, name='verify_otp'),
    path('change_email/', views.change_email, name='change_email'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('forgot_password/', views.forget_password, name='forgor_password'),
    path('forgot_password_verify_otp/', views.forgot_password_verify_otp, name='forgor_password_otp'),   
    path('forgot_password_change/', views.forgot_password_change, name='forgor_password_change'),
]
