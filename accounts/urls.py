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
from .views import UserProfileViewSet
router = DefaultRouter()
router.register('profile', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('normal_register/', normal_register, name='register'),
    path('varify_otp/', verify_otp, name='verify_otp'),
    path('logout/', logout_view, name='logout'),
    
]
