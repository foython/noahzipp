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



@extend_schema(request=AppointmentsSerializer, responses={201: AppointmentsSerializer})
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_appointment_view(request, pk=None):
    if request.method == 'GET':
        if pk is None:
            user_services = Services.objects.filter(user=request.user)
            appointments = Appointments.objects.filter(service__in=user_services)
            serializer = AppointmentsSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                appointment = Appointments.objects.get(pk=pk, service__user=request.user)
                serializer = AppointmentsSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointments.DoesNotExist:
                return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        serializer = AppointmentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = serializer.validated_data['service']
            service_provider = service.user
        except Services.DoesNotExist:
            return Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

      
        user = service_provider
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
       
        
        subscription_status = user.subscription_status if hasattr(user, 'subscription_status') else None
        print(subscription_status)
        appointment_limit = 0
        if subscription_status == 'Monthly':
            appointment_limit = 1
        elif subscription_status == 'Quarterly':
            appointment_limit = 150
        elif subscription_status == 'Yearly':
            appointment_limit = 600
        
        if appointment_limit > 0:
          
            appointment_count = Appointments.objects.filter(
                service__user=user,
                created_at__gte=current_month_start
            ).count()
            
            if appointment_count >= appointment_limit:
                return Response(
                    {"detail": "Your package has a limit of {} appointments. Please upgrade your package to add more.".format(appointment_limit)},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        requested_date = serializer.validated_data['date']
        requested_time_str = serializer.validated_data['time']

        try:
            requested_time = datetime.strptime(requested_time_str, '%I:%M %p').time()
        except ValueError:
            return Response({"time": "Invalid time format. Please use 'hh:mm AM/PM' (e.g., '02:30 PM')."}, status=status.HTTP_400_BAD_REQUEST)

        requested_datetime = datetime.combine(requested_date, requested_time)
        
        try:
            user_availability = User_avalablity.objects.get(user=service_provider)
            appointment_duration = user_availability.time_slot_duration
        except User_avalablity.DoesNotExist:
            appointment_duration = 30 
        
        requested_end_datetime = requested_datetime + timedelta(minutes=appointment_duration)

       
        unavailability_periods = User_unavailability.objects.filter(
            user=service_provider,
            from_date__lte=requested_date,
            to_date__gte=requested_date
        )

        for period in unavailability_periods:
            try:
                unavailability_start = datetime.combine(period.from_date, datetime.strptime(period.from_time, '%I:%M %p').time())
                unavailability_end = datetime.combine(period.to_date, datetime.strptime(period.to_time, '%I:%M %p').time())
            except ValueError:
                continue
                
            if (requested_datetime < unavailability_end) and (requested_end_datetime > unavailability_start):
                return Response(
                    {"detail": f"User is unavailable from {unavailability_start.strftime('%Y-%m-%d %I:%M %p')} to {unavailability_end.strftime('%Y-%m-%d %I:%M %p')}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Check for overlapping appointments
        existing_appointments = Appointments.objects.filter(
            service__user=service_provider,
            date=requested_date,
            status='ACTIVE'
        )

        for existing_appointment in existing_appointments:
            try:
                existing_availability = User_avalablity.objects.get(user=service_provider)
                existing_duration = existing_availability.time_slot_duration
            except User_avalablity.DoesNotExist:
                existing_duration = 30

            existing_start_time = datetime.combine(existing_appointment.date, datetime.strptime(existing_appointment.time, '%I:%M %p').time())
            existing_end_time = existing_start_time + timedelta(minutes=existing_duration)
            
            if (requested_datetime < existing_end_time) and (requested_end_datetime > existing_start_time):
                return Response({"detail": "This time slot overlaps with an existing appointment."}, status=status.HTTP_400_BAD_REQUEST)

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



@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_notification_view(request):
    if request.method == 'GET':
        # Retrieve all notifications for the current user
        queryset = user_notification.objects.filter(user=request.user).order_by('-created_at')         
            
        serializer = UserNotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        
        unread_notifications = user_notification.objects.filter(user=request.user, is_read=False)
        updated_count = unread_notifications.update(is_read=True)
        
        return Response(
            {"detail": f"{updated_count} notifications have been marked as read."},
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