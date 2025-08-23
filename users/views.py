from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Chatbot, Services, Appointments
from .serializers import ChatbotSerializer, ServicesSerializer, AppointmentsSerializer
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth


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
        



@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_services(request, pk=None):
   
    if request.method == 'GET':
        if pk is None:            
            services = Services.objects.filter(chatbot__owner=request.user)
            serializer = ServicesSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:                
                service = Services.objects.get(pk=pk, chatbot__owner=request.user)
                serializer = ServicesSerializer(service)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Services.DoesNotExist:
                return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        # Create a new service, validating that the chatbot belongs to the user
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            # Get the chatbot ID from the validated data
            chatbot_id = serializer.validated_data.get('chatbot').id
            try:
                # Fetch the chatbot object using the ID and check for ownership
                chatbot = Chatbot.objects.get(pk=chatbot_id, owner=request.user)
                # The serializer's save method will automatically save the chatbot instance
                # that was passed during validation. We don't need to pass it again.
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Chatbot.DoesNotExist:
                return Response({"error": "Chatbot not found or you don't have permission to use it."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/PATCH/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Check ownership before allowing update/delete
            service = Services.objects.get(pk=pk, chatbot__owner=request.user)
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




@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_appointments(request, pk=None):
    if request.method == 'GET':
        if pk is None:
            appointments = Appointments.objects.filter(service__chatbot__owner=request.user)
            serializer = AppointmentsSerializer(appointments, many=True)
            if not appointments.exists():
                return Response({"message": "You have no appointments at this time."}, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                appointment = Appointments.objects.get(pk=pk, service__chatbot__owner=request.user)
                serializer = AppointmentsSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointments.DoesNotExist:
                return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        serializer = AppointmentsSerializer(data=request.data)
        if serializer.is_valid():
            service_id = serializer.validated_data.get('service').id
            try:
                Services.objects.get(pk=service_id, chatbot__owner=request.user)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Services.DoesNotExist:
                return Response({"error": "You don't have permission to create appointments for this service."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/PATCH/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment = Appointments.objects.get(pk=pk, service__chatbot__owner=request.user)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PUT':
            serializer = AppointmentsSerializer(appointment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = AppointmentsSerializer(appointment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_appointments_api_view(request):
   
    two_years_ago = datetime.now() - timedelta(days=730)

   
    appointments_by_month = Appointments.objects.filter(
        date__gte=two_years_ago,
        service__chatbot__owner=request.user
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
    """
    API endpoint that returns a summary count of appointments for Today,
    the Last Month, and the Current Month, for the authenticated user.
    """
    # Get the current date and time
    today = datetime.now().date()
    
    # Calculate the start and end dates for the current month
    start_of_current_month = today.replace(day=1)
    
    # Calculate the start and end dates for the last month
    end_of_last_month = start_of_current_month - timedelta(days=1)
    start_of_last_month = end_of_last_month.replace(day=1)

    # Perform the counts for each period, filtered by the authenticated user
    today_count = Appointments.objects.filter(
        service__chatbot__owner=request.user,
        date=today
    ).count()

    current_month_count = Appointments.objects.filter(
        service__chatbot__owner=request.user,
        date__gte=start_of_current_month
    ).count()

    last_month_count = Appointments.objects.filter(
        service__chatbot__owner=request.user,
        date__gte=start_of_last_month,
        date__lte=end_of_last_month
    ).count()

    # Create a dictionary to hold the counts
    summary_data = {
        'today_appointments': today_count,
        'last_month_appointments': last_month_count,
        'current_month_appointments': current_month_count,
    }

    return Response(summary_data, status=status.HTTP_200_OK)
