from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Chatbot, Services, Appointments
from .serializers import ChatbotSerializer, ServicesSerializer, AppointmentsSerializer



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
        



@api_view(['GET', 'POST', 'PUT', 'DELETE'])
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


    elif request.method in ['PUT', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Check ownership before allowing update/delete
            service = Services.objects.get(pk=pk, chatbot__owner=request.user)
        except Services.DoesNotExist:
            return Response({"error": "Service not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'PUT':
            serializer = ServicesSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            service.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        



@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_appointments(request, pk=None):
    if request.method == 'GET':
        if pk is None:            
            appointments = Appointments.objects.filter(service__owner=request.user)
            serializer = AppointmentsSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:                
                appointment = Appointments.objects.get(pk=pk, service__owner=request.user)
                serializer = AppointmentsSerializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointments.DoesNotExist:
                return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        serializer = AppointmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method in ['PUT', 'DELETE']:
        if pk is None:
            return Response({"error": "A primary key is required for PUT/DELETE."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment = Appointments.objects.get(pk=pk, service__owner=request.user)
        except Appointments.DoesNotExist:
            return Response({"error": "Appointment not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PUT':
            serializer = AppointmentsSerializer(appointment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)