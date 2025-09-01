from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.models import Chatbot
from rest_framework import status
from .ai import booking_assistant
from users.models import Services, Appointments, User_avalablity, User_unavailability, service_discount, Chatbot
from users.serializers import ServicesSerializer, ServiceDiscountSerializer, AppointmentsSerializer, UserAvailabilitySerializer, UserUnavailabilitySerializer, ChatbotSerializer
from datetime import datetime
from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer
import json
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime


@api_view(['POST'])
def send_message(request, unique_id):
    current_datetime = datetime.now()
    try:
        previous_conversation = request.data.get('previous_conversation')
        message = request.data.get('message')
        
        if not message or not unique_id:
            return Response({"error": "Message and unique_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use get_object_or_404 for clean error handling
        chat_bot = get_object_or_404(Chatbot, pk=unique_id)
        
        chating_style = chat_bot.chatting_style
        
        # Get and serialize user availability data
        availability_queryset = User_avalablity.objects.filter(user=chat_bot.owner.id)
        user_availability_data = UserAvailabilitySerializer(availability_queryset, many=True).data
        
        # Get services and their IDs
        services_queryset = Services.objects.filter(user=chat_bot.owner.id)
        service_ids = services_queryset.values_list('id', flat=True)
        services_data = ServicesSerializer(services_queryset, many=True).data
        
        user = CustomUser.objects.get(id=chat_bot.owner.id)
        professional_background = user.professional_background
        
        # Filter appointments using the list of service IDs
        appointments_queryset = Appointments.objects.filter(service__in=service_ids)
        appointments_data = AppointmentsSerializer(appointments_queryset, many=True).data

        # Call the booking assistant function with all necessary data
        bot_response_json = booking_assistant(
            current_datetime, 
            message, 
            chating_style, 
            previous_conversation, 
            user_availability_data, 
            appointments_data, 
            services_data, 
            chat_bot.name, 
            professional_background
        )
        
        # Parse the JSON response from the chatbot
        bot_response_dict = json.loads(bot_response_json)
        response = bot_response_dict["response"]
        
        # Conditionally save the appointment if confirmed
        confirmed_booking = bot_response_dict.get("confirmed_booking", "no")
        if confirmed_booking.lower() == 'yes':
            try:
                # Retrieve the correct service instance
                service = Services.objects.get(id=bot_response_dict["service_id"])
                
                # Create and save a new Appointments instance
                new_appointment = Appointments.objects.create(
                    service=service,
                    customer_name=bot_response_dict.get("customer_name"),
                    contact_number=bot_response_dict.get("contact_number", ""),
                    customer_email=bot_response_dict.get("customer_email", ""),
                    service_description=bot_response_dict.get("service_description", ""),
                    # Ensure the date string matches the format '%Y-%m-%d'
                    date=datetime.strptime(bot_response_dict.get("date"), '%Y-%m-%d').date(), 
                    time=bot_response_dict.get("time"),
                    about=bot_response_dict.get("about", ""), # Assumed a field in model
                    status='ACTIVE'
                )
                print(f'New appointment created: {new_appointment}')
            except Services.DoesNotExist:
                return Response({"error": "Service for the booking was not found."}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, KeyError) as e:
                # Catch specific errors for missing keys or incorrect date/time format
                return Response({"error": f"Booking data is incomplete or invalid: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the final response to the client
        data = {
            "bot_response": response,
            "image": f"http://localhost:5000/{chat_bot.logo.url}"
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON from bot_response"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # A general catch-all for any other unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_embedding(request):
    try:
        user = request.user
        bot = Chatbot.objects.get(owner=user)
        embed_code = f'<script src="hhttp://localhost:5000/static/chatbot.js" data-token="{bot.pk}"></script>'
        return Response(
            {
                "embed_link": embed_code
            },
            status=200
        )
    except:
        return Response(
            {
                "Error": "No Chatbot Created yet."
            },
            status=400
        )