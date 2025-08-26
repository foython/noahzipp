from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Chatbot, Services, Appointments, service_discount, User_avalablity
from .serializers import ChatbotSerializer, ServicesSerializer, AppointmentsSerializer, ServiceDiscountSerializer, UserAvailabilitySerializer
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from drf_spectacular.utils import extend_schema
from django.db import IntegrityError

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



@extend_schema(request=AppointmentsSerializer,responses={201: AppointmentsSerializer},)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_appointment_view(request, pk=None):
 
    if request.method == 'GET':
        if pk is None:
            appointments = Appointments.objects.all()
            serializer = AppointmentsSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                appointment = Appointments.objects.get(pk=pk)
                serializer = AppointmentsSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointments.DoesNotExist:
                return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        serializer = AppointmentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = serializer.validated_data['service']
            service_provider = service.user
            provider_availability = User_avalablity.objects.get(user=service_provider)
        except Services.DoesNotExist:
            return Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        except User_avalablity.DoesNotExist:
            return Response({"detail": "Service provider has not set their availability."}, status=status.HTTP_400_BAD_REQUEST)
        
        requested_date = serializer.validated_data['date']
        requested_time_str = serializer.validated_data['time']

        try:
            requested_time = datetime.strptime(requested_time_str, '%I:%M %p').time()
        except ValueError:
            return Response({"time": "Invalid time format. Please use 'hh:mm AM/PM' (e.g., '02:30 PM')."}, status=status.HTTP_400_BAD_REQUEST)

        requested_datetime = datetime.combine(requested_date, requested_time)
        time_slot_duration = provider_availability.time_slot_duration
        requested_end_datetime = requested_datetime + timedelta(minutes=time_slot_duration)

        try:
            from_time = datetime.strptime(provider_availability.from_time, '%I:%M %p').time()
            to_time = datetime.strptime(provider_availability.to_time, '%I:%M %p').time()
        except ValueError:
            return Response({"detail": "Service provider's availability times are in an invalid format."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        requested_day = requested_date.strftime('%A')
        
        # FIX: Normalize both the requested day and the list of available days to lowercase.
        normalized_available_days = [day.lower() for day in provider_availability.days]
        if requested_day.lower() not in normalized_available_days:
            return Response({"detail": f"Service provider is not available on {requested_day}s."}, status=status.HTTP_400_BAD_REQUEST)
        
        provider_from_datetime = datetime.combine(requested_date, from_time)
        provider_to_datetime = datetime.combine(requested_date, to_time)
        
        if not (provider_from_datetime <= requested_datetime < provider_to_datetime):
            return Response({"detail": "The requested time is outside the service provider's available hours."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check for overlapping appointments
        existing_appointments = Appointments.objects.filter(
            service__user=service_provider,
            date=requested_date,
            status='ACTIVE'
        )

        for existing_appointment in existing_appointments:
            try:
                existing_start_time = datetime.combine(existing_appointment.date, datetime.strptime(existing_appointment.time, '%I:%M %p').time())
            except (TypeError, ValueError):
                continue
            
            existing_end_time = existing_start_time + timedelta(minutes=time_slot_duration)
            
            if (requested_datetime < existing_end_time) and (requested_end_datetime > existing_start_time):
                return Response({"detail": "This time slot overlaps with an existing appointment."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment = Appointments.objects.get(pk=pk)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AppointmentsSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment = Appointments.objects.get(pk=pk)
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)


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
    """
    Handles user availability using GET and POST methods, with POST
    using a more efficient update_or_create pattern.
    """
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
                # Use update_or_create to handle both cases efficiently
                # This looks up by 'user' and updates with all validated data.
                availability, created = User_avalablity.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'days': serializer.validated_data.get('days'),
                        'from_time': serializer.validated_data.get('from_time'),
                        'to_time': serializer.validated_data.get('to_time'),
                        'time_slot_duration': serializer.validated_data.get('time_slot_duration')
                    }
                )
                
                # Re-serialize the created/updated instance to return the full data
                response_serializer = UserAvailabilitySerializer(availability)
                
                # Return 201 Created for new instances, 200 OK for updates
                response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response(response_serializer.data, status=response_status)
            
            except IntegrityError:
                return Response({"detail": "An integrity error occurred."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)