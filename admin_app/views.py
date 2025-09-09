from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import PrivacyPolicy, FAQ
from .serializers import PrivacyPolicySerializer, FAQSerializer, AdminNotificationSerializer
from rest_framework import permissions
from datetime import datetime, timedelta
from .models import AdminNotification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import CustomUser 
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()




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





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_statistics(request):

    if request.user.role != 'ADMIN':
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)
   
    if request.method == 'GET':

        try:            
            total_subscribers = CustomUser.objects.filter(is_subscribed=True).count()            
            
            total_on_hold_accounts = CustomUser.objects.filter(status='HOLD').count()            
           
            total_active_users = CustomUser.objects.filter(status='ACTIVE').count()            
            
            data = {
                'total_subscribers': total_subscribers,
                'total_on_hold_accounts': total_on_hold_accounts,
                'total_active_users': total_active_users,
            }
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:           
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_notification_view(request, pk=None):
    if request.user.role != 'ADMIN':
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
       
        queryset = AdminNotification.objects.filter().order_by('-created_at')         
            
        serializer = AdminNotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        
        unread_notifications = AdminNotification.objects.filter(is_read=False)
        updated_count = unread_notifications.update(is_read=True)
        
        return Response(
            {"detail": f"{updated_count} notifications have been marked as read."},
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        if pk:            
            try:
                notification_to_delete = AdminNotification.objects.get(pk=pk)
                notification_to_delete.delete()
                return Response(
                    {"detail": f"Notification with ID {pk} successfully deleted."},
                    status=status.HTTP_200_OK
                )
            except AdminNotification.DoesNotExist:
                return Response(
                    {"detail": f"Notification with ID {pk} not found or does not belong to the user."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:          
            deleted_count, _ = AdminNotification.objects.filter().delete()
            
            return Response(
                {"detail": f"Successfully deleted {deleted_count} notifications."},
                status=status.HTTP_200_OK
            )




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_user_registrations_api_view(request):
    two_years_ago = datetime.now() - timedelta(days=730)

    user_registrations_by_month = CustomUser.objects.filter(
        created_at__gte=two_years_ago
    ).annotate(
        month=TruncMonth('date_joined')
    ).values(
        'month'
    ).annotate(
        count=Count('id')
    ).order_by(
        'month'
    )

    serialized_data = list(user_registrations_by_month)

    return Response(serialized_data, status=status.HTTP_200_OK)