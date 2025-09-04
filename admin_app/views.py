from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import PrivacyPolicy, FAQ
from .serializers import PrivacyPolicySerializer, FAQSerializer
from rest_framework import permissions




class IsAdminRole(permissions.BasePermission):   
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class PrivacyPolicyViewSet(viewsets.ModelViewSet):    
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    permission_classes = [IsAdminRole]

class FAQViewSet(viewsets.ModelViewSet):    
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminRole]



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import CustomUser # Assuming CustomUser is the name of your user model

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_statistics(request):
    
    if request.user.role != 'ADMIN':
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)
   
    if request.method == 'GET':

        try:
            # Count users with is_subscribed set to True.
            total_subscribers = CustomUser.objects.filter(is_subscribed=True).count()
            
            # Count users with a status of 'HOLD'.
            total_on_hold_accounts = CustomUser.objects.filter(status='HOLD').count()
            
            # Count users with a status of 'ACTIVE'.
            total_active_users = CustomUser.objects.filter(status='ACTIVE').count()
            
            # Create a dictionary to hold the statistics.
            data = {
                'total_subscribers': total_subscribers,
                'total_on_hold_accounts': total_on_hold_accounts,
                'total_active_users': total_active_users,
            }
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle potential errors, such as database connection issues.
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)