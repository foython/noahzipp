from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import PrivacyPolicy, FAQ
from .serializers import PrivacyPolicySerializer, FAQSerializer
from rest_framework import permissions




class IsAdminRole(permissions.BasePermission):
    """
    Custom permission to allow only users with the 'ADMIN' role to access views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

# ViewSets for PrivacyPolicy and FAQ
class PrivacyPolicyViewSet(viewsets.ModelViewSet):
    """
    API viewset for Privacy Policy, supporting all CRUD operations.
    """
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    permission_classes = [IsAdminRole]

class FAQViewSet(viewsets.ModelViewSet):
    """
    API viewset for FAQ, supporting all CRUD operations.
    """
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminRole]