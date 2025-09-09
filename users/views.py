from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Chatbot, Services, Appointments, service_discount, User_avalablity, user_notification
from .serializers import ChatbotSerializer, ServicesSerializer, AppointmentsSerializer, ServiceDiscountSerializer, UserAvailabilitySerializer, UserUnavailabilitySerializer, User_unavailability, UserNotificationSerializer
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from drf_spectacular.utils import extend_schema
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .models import user_notification

@extend_schema(request=ChatbotSerializer,responses={201: ChatbotSerializer},)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_chatbots(request, pk=None):
  
    if request.method == 'GET':
        if pk is None:            
            chatbots = Chatbot.objects.filter(owner=request.user)
            serializer = ChatbotSerializer(chatbots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                chatbot = Chatbot.objects.get(pk=pk, owner=request.user)
                serializer = ChatbotSerializer(chatbot)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Chatbot.DoesNotExist:
                return Response({"error": "Chatbot not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
    
    
    elif request.method == 'POST':
        user = request.user
        owner = Chatbot.objects.filter(owner=user)

        if owner.count() > 0:
            owner = owner[0]
            serializer = ChatbotSerializer(owner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = ChatbotSerializer(data=request.data)
            if serializer.is_valid():
                
                serializer.save(owner=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    elif request.method in ['PUT', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            chatbot = Chatbot.objects.get(pk=pk, owner=request.user)
        except Chatbot.DoesNotExist:
            return Response({"error": "Chatbot not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PUT':
            serializer = ChatbotSerializer(chatbot, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            chatbot.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    


@extend_schema(request=ServicesSerializer,responses={201: ServicesSerializer},)
@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_services(request, pk=None):
   
    if request.method == 'GET':
        if pk is None:
            services = Services.objects.filter(user=request.user)
            serializer = ServicesSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                service = Services.objects.get(pk=pk, user=request.user)
                serializer = ServicesSerializer(service)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Services.DoesNotExist:
                return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        print("Received POST request data:", request.data) # <-- Add this line
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid!") # <-- Add this line
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors) # <-- Add this line
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/PATCH/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = Services.objects.get(pk=pk, user=request.user)
        except Services.DoesNotExist:
            return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'PUT':
            serializer = ServicesSerializer(service, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = ServicesSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            service.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        

        
@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_discounts(request, pk=None):
   
    if request.method == 'GET':
        service_id = request.query_params.get('service_id', None)
        if pk is None:
            if service_id is None:
                return Response({"error": "Service ID is required for listing discounts."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                service = Services.objects.get(pk=service_id, user=request.user)
                discounts = service_discount.objects.filter(service=service)
                serializer = ServiceDiscountSerializer(discounts, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Services.DoesNotExist:
                return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                discount = service_discount.objects.get(pk=pk, service__user=request.user)
                serializer = ServiceDiscountSerializer(discount)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except service_discount.DoesNotExist:
                return Response({"error": "Discount not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        serializer = ServiceDiscountSerializer(data=request.data)
        if serializer.is_valid():
            service_id = serializer.validated_data.get('service').id
            try:
                service = Services.objects.get(pk=service_id, user=request.user)
                serializer.save(service=service)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Services.DoesNotExist:
                return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/PATCH/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount = service_discount.objects.get(pk=pk, service__user=request.user)
        except service_discount.DoesNotExist:
            return Response({"error": "Discount not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'PUT':
            serializer = ServiceDiscountSerializer(discount, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = ServiceDiscountSerializer(discount, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            discount.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        


from .utils import validate_appointment_creation



@extend_schema(request=AppointmentsSerializer, responses={201: AppointmentsSerializer})
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_appointment_view(request, pk=None):
    if request.method == 'GET':
        if pk is None:
            
            user_services = Services.objects.filter(user=request.user)
            
            appointments = Appointments.objects.filter(service__in=user_services)

            paginator = PageNumberPagination()
            paginator.page_size = 10 

           
            paginated_appointments = paginator.paginate_queryset(appointments, request)

           
            serializer = AppointmentsSerializer(paginated_appointments, many=True)
            
            return paginator.get_paginated_response(serializer.data)
        else:
            try:
                
                appointment = Appointments.objects.get(pk=pk, service__user=request.user)
                serializer = AppointmentsSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointments.DoesNotExist:
                return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)


    elif request.method == 'POST':
        try:
            service = Services.objects.get(pk=request.data.get('service'))
            service_provider = service.user
        except Services.DoesNotExist:
            return Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        validation_response = validate_appointment_creation(serializer.validated_data, service_provider)
        
        
        if validation_response:
            return validation_response

        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'PUT':
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment = Appointments.objects.get(pk=pk, service__user=request.user)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AppointmentsSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            notification = user_notification.objects.create(user=appointment.service.user, message=f'New Appointment Booked at {appointment.date}')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment = Appointments.objects.get(pk=pk, service__user=request.user)
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_appointments_api_view(request):
  
    two_years_ago = datetime.now() - timedelta(days=730)

    appointments_by_month = Appointments.objects.filter(
        date__gte=two_years_ago,        
        service__user=request.user
    ).annotate(
        month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        count=Count('id')
    ).order_by(
        'month'
    )

    serialized_data = list(appointments_by_month)

    return Response(serialized_data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_summary_api_view(request):
    
    today = datetime.now().date()
    
    
    start_of_current_month = today.replace(day=1)
    
    
    end_of_last_month = start_of_current_month - timedelta(days=1)
    start_of_last_month = end_of_last_month.replace(day=1)

    
    today_count = Appointments.objects.filter(
        service__user=request.user,
        date=today
    ).count()

    current_month_count = Appointments.objects.filter(
        service__user=request.user, 
        date__gte=start_of_current_month
    ).count()

    last_month_count = Appointments.objects.filter(
        service__user=request.user, 
        date__gte=start_of_last_month,
        date__lte=end_of_last_month
    ).count()

   
    summary_data = {
        'today_appointments': today_count,
        'last_month_appointments': last_month_count,
        'current_month_appointments': current_month_count,
    }

    return Response(summary_data, status=status.HTTP_200_OK)




@extend_schema(request=UserAvailabilitySerializer, responses={201: UserAvailabilitySerializer})
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_availability_view(request):

    if request.method == 'GET':
        try:
            availability = User_avalablity.objects.get(user=request.user)
            serializer = UserAvailabilitySerializer(availability)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User_avalablity.DoesNotExist:
            return Response(
                {"detail": "User availability not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    elif request.method == 'POST':
        serializer = UserAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            try:
                
                availability, created = User_avalablity.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'days': serializer.validated_data.get('days'),
                        'from_time': serializer.validated_data.get('from_time'),
                        'to_time': serializer.validated_data.get('to_time'),
                        'time_slot_duration': serializer.validated_data.get('time_slot_duration')
                    }
                )
                
                
                response_serializer = UserAvailabilitySerializer(availability)
                
                response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response(response_serializer.data, status=response_status)
            
            except IntegrityError:
                return Response({"detail": "An integrity error occurred."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    
@extend_schema(request=UserUnavailabilitySerializer, responses={201: UserUnavailabilitySerializer})
@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def set_unavailability_view(request, pk=None):  
    
    
    if request.method == 'POST':
        
        serializer = UserUnavailabilitySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from_date = serializer.validated_data['from_date']
        from_time_str = serializer.validated_data['from_time']
        to_date = serializer.validated_data['to_date']
        to_time_str = serializer.validated_data['to_time']

        from_datetime = datetime.combine(from_date, datetime.strptime(from_time_str, '%I:%M %p').time())
        to_datetime = datetime.combine(to_date, datetime.strptime(to_time_str, '%I:%M %p').time())

        
        active_appointments = Appointments.objects.filter(
            service__user=request.user,
            status='ACTIVE'
        )

        for appointment in active_appointments:
            try:
                appointment_start_datetime = datetime.combine(appointment.date, datetime.strptime(appointment.time, '%I:%M %p').time())
            except (ValueError, TypeError):
                continue
                
            appointment_duration = 30  
            appointment_end_datetime = appointment_start_datetime + timedelta(minutes=appointment_duration)

            if (from_datetime < appointment_end_datetime) and (to_datetime > appointment_start_datetime):
                return Response(
                    {"detail": "Cannot set unavailability. There is an existing appointment during this time period."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        conflicting_unavailability = User_unavailability.objects.filter(
            Q(user=request.user) &
            (Q(from_date__lt=to_date) & Q(to_date__gt=from_date))
        )
        
        for existing_period in conflicting_unavailability:
            existing_start_datetime = datetime.combine(existing_period.from_date, datetime.strptime(existing_period.from_time, '%I:%M %p').time())
            existing_end_datetime = datetime.combine(existing_period.to_date, datetime.strptime(existing_period.to_time, '%I:%M %p').time())

            if (from_datetime < existing_end_datetime) and (to_datetime > existing_start_datetime):
                return Response(
                    {"detail": "Cannot set unavailability. It conflicts with a previously set unavailability period."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        
        user_unavailability_periods = User_unavailability.objects.filter(user=request.user).order_by('-from_date')
        serializer = UserUnavailabilitySerializer(user_unavailability_periods, many=True)
        return Response(serializer.data)

 
    elif request.method == 'PATCH':
        if not pk:
            return Response({"detail": "Method PATCH requires a primary key (pk) in the URL."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = User_unavailability.objects.get(pk=pk, user=request.user)
        except User_unavailability.DoesNotExist:
            return Response({"detail": "Unavailability period not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUnavailabilitySerializer(instance, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract dates and times for conflict checking
        from_date = serializer.validated_data.get('from_date', instance.from_date)
        from_time_str = serializer.validated_data.get('from_time', instance.from_time)
        to_date = serializer.validated_data.get('to_date', instance.to_date)
        to_time_str = serializer.validated_data.get('to_time', instance.to_time)

        from_datetime = datetime.combine(from_date, datetime.strptime(from_time_str, '%I:%M %p').time())
        to_datetime = datetime.combine(to_date, datetime.strptime(to_time_str, '%I:%M %p').time())
        
        # Check for conflicts with existing active appointments (same logic as POST)
        active_appointments = Appointments.objects.filter(
            service__user=request.user,
            status='ACTIVE'
        )

        for appointment in active_appointments:
            try:
                appointment_start_datetime = datetime.combine(appointment.date, datetime.strptime(appointment.time, '%I:%M %p').time())
            except (ValueError, TypeError):
                continue
                
            appointment_duration = 30  # Assuming 30 minutes
            appointment_end_datetime = appointment_start_datetime + timedelta(minutes=appointment_duration)

            if (from_datetime < appointment_end_datetime) and (to_datetime > appointment_start_datetime):
                return Response(
                    {"detail": "Cannot update unavailability. There is an existing appointment during this time period."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Check for conflicts with existing unavailability periods (excluding the current one)
        conflicting_unavailability = User_unavailability.objects.filter(
            Q(user=request.user) &
            ~Q(pk=instance.pk) & # Exclude the instance being updated
            (Q(from_date__lt=to_date) & Q(to_date__gt=from_date))
        )
        
        for existing_period in conflicting_unavailability:
            existing_start_datetime = datetime.combine(existing_period.from_date, datetime.strptime(existing_period.from_time, '%I:%M %p').time())
            existing_end_datetime = datetime.combine(existing_period.to_date, datetime.strptime(existing_period.to_time, '%I:%M %p').time())

            if (from_datetime < existing_end_datetime) and (to_datetime > existing_start_datetime):
                return Response(
                    {"detail": "Cannot update unavailability. It conflicts with a previously set unavailability period."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        if not pk:
            return Response({"detail": "Method DELETE requires a primary key (pk) in the URL."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = User_unavailability.objects.get(pk=pk, user=request.user)
        except User_unavailability.DoesNotExist:
            return Response({"detail": "Unavailability period not found."}, status=status.HTTP_404_NOT_FOUND)
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_notification_view(request, pk=None):
    
    if request.method == 'GET':
        # Retrieve all notifications for the authenticated user, ordered by creation date.
        queryset = user_notification.objects.filter(user=request.user).order_by('-created_at')         
        serializer = UserNotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        # Mark all unread notifications for the user as read.
        unread_notifications = user_notification.objects.filter(user=request.user, is_read=False)
        updated_count = unread_notifications.update(is_read=True)
        
        return Response(
            {"detail": f"{updated_count} notifications have been marked as read."},
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        if pk:
            # Delete a specific notification by ID for the authenticated user.
            try:
                notification_to_delete = user_notification.objects.get(pk=pk, user=request.user)
                notification_to_delete.delete()
                return Response(
                    {"detail": f"Notification with ID {pk} successfully deleted."},
                    status=status.HTTP_200_OK
                )
            except user_notification.DoesNotExist:
                return Response(
                    {"detail": f"Notification with ID {pk} not found or does not belong to the user."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Delete all notifications for the authenticated user.
            deleted_count, _ = user_notification.objects.filter(user=request.user).delete()
            
            return Response(
                {"detail": f"Successfully deleted {deleted_count} notifications."},
                status=status.HTTP_200_OK
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chatbot_id(request):
    if request.method == 'GET':
        try:
            chatbot = Chatbot.objects.get(owner=request.user)
            # Return a response with only the chatbot's ID
            return Response({"id": chatbot.pk}, status=status.HTTP_200_OK)
        except Chatbot.DoesNotExist:
            return Response({"error": "Chatbot not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

from datetime import datetime
from django.utils import timezone



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_appointments(request):
   
    try:
        user_services = Services.objects.filter(user=request.user)
        current_datetime = timezone.now()

        recent_appointments = Appointments.objects.filter(
            service__in=user_services,
            date__gte = datetime.today()
        ).order_by('-created_at')
     
        paginator = PageNumberPagination()
        paginator.page_size = 10         
        paginated_queryset = paginator.paginate_queryset(recent_appointments, request)    
         
        serializer = AppointmentsSerializer(paginated_queryset, many=True)

       
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from .models import Appointments


@api_view(['PATCH'])
def cancel_appointment_status(request, pk):
    
    appointment = get_object_or_404(Appointments, pk=pk)
    old_status = appointment.status
    if appointment.service.user != request.user:
        return Response(
            {"message": "You are not authorized to reschedule this appointment."},
            status=status.HTTP_403_FORBIDDEN
        )

    new_status = request.data.get('status')
    cancel_reason = request.data.get('cancel_reason')

    if new_status:
        appointment.status = new_status
    if cancel_reason is not None:
        appointment.cancel_reason = cancel_reason
    
    appointment.save(update_fields=['status', 'cancel_reason'])

   
    if appointment.status != old_status:
        
        
        if appointment.status == 'CANCELED':
            subject = 'Your Appointment Has Been Canceled'            
            message = f'Dear {appointment.customer_name}, This is to inform you that your appointment for **{ appointment.service.service_name }** on { appointment.date } at { appointment.time } has been **CANCELED** for {cancel_reason}.'
            from_email = 'support@gameplanai.co.uk'
            recipient_list = [appointment.customer_email]

            email_message = EmailMessage(subject, message, from_email, recipient_list)
            email_message.send()     
        
            return Response(
                {"message": "Appointment updated successfully and email sent."},
                status=status.HTTP_200_OK
            )
    else:
        return Response({"message": f"your appointment status is already {appointment.status }"},
            status=status.HTTP_200_OK)
    

@api_view(['PATCH'])
def reschedule_appointment_status(request, pk):
    appointment = get_object_or_404(Appointments, pk=pk)
    old_status = appointment.status

    if old_status == 'CANCELED':
        return Response(
            {"message": "You are not allowed to reschedule a canceled appointment."},
            status=status.HTTP_403_FORBIDDEN
        )

    if appointment.service.user != request.user:
        return Response(
            {"message": "You are not authorized to reschedule this appointment."},
            status=status.HTTP_403_FORBIDDEN
        )

    
    new_status = request.data.get('status')
    reschedule_reason = request.data.get('reschedule_reason')
    reschedule_date = request.data.get('date')
    reschedule_time = request.data.get('time')

    
    update_data = {
        'status': new_status,
        'date': reschedule_date,
        'time': reschedule_time,
        'reschedule_reason': reschedule_reason,
        'reschedule': True if new_status == 'RESCHEDULED' else appointment.reschedule 
    }

   
    serializer = AppointmentsSerializer(appointment, data=update_data, partial=True)

   
    if serializer.is_valid():
        
        serializer.save()

       
        if appointment.status == 'RESCHEDULED':
            subject = 'Your Appointment Has Been Rescheduled'
            message = f'Dear {appointment.customer_name}, This is to inform you that your appointment for **{ appointment.service.service_name }** on { appointment.date } at { appointment.time } has been **RESCHEDULED**. Reason: {reschedule_reason}.'
            from_email = 'support@gameplanai.co.uk'
            recipient_list = [appointment.customer_email]

            email_message = EmailMessage(subject, message, from_email, recipient_list)
            try:
                email_message.send()
                return Response(
                    {"message": "Appointment updated successfully and email sent."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                
                return Response(
                    {"message": f"Appointment updated, but failed to send email. Error: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            
            return Response(
                {"message": f"Your appointment status is already {appointment.status }."},
                status=status.HTTP_200_OK
            )
    else:
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
