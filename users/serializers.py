from rest_framework import serializers
from .models import Chatbot, Services, Appointments, service_discount, User_avalablity
from datetime import datetime

class ChatbotSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chatbot
        fields = [
            'id', 'owner', 'name', 'chatting_style', 'description', 'logo'
        ]
        read_only_fields = ['owner'] 



class ServiceDiscountSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = service_discount
        fields = [
            'id', 'service', 'discount_price', 'discount_deadline', 'status'
        ]

class ServicesSerializer(serializers.ModelSerializer):
    # Change the field name to 'service_discount' to match the related_name
    service_discount = ServiceDiscountSerializer(many=True, read_only=True)
    
    class Meta:
        model = Services
        fields = [
            'id', 'user', 'service_name', 'Description_of_service', 'price',
            'status', 'service_discount' # Also update the field list here
        ]
        read_only_fields = ['user'] 


class AppointmentsSerializer(serializers.ModelSerializer):
  
    class Meta:
        
        model = Appointments
        
        
        fields = [
            'id', 
            'service', 
            'Description_of_service', 
            'customer', 
            'contact', 
            'date', 
            'time', 
            'about', 
            'status'
        ]


class UserAvailabilitySerializer(serializers.ModelSerializer):
  
    
    class Meta:
       
        model = User_avalablity
        
        fields = ['id', 'days', 'from_time', 'to_time', 'time_slot_duration']

    def validate(self, data):
        """
        Validate that the 'to_time' is after the 'from_time'.
        """
        from_time_str = data.get('from_time')
        to_time_str = data.get('to_time')
        
        # Check if both times are present for comparison
        if from_time_str and to_time_str:
            # Convert string times to datetime.time objects for comparison
            # The format string matches the validator's expected format
            from_time = datetime.strptime(from_time_str, '%I:%M %p').time()
            to_time = datetime.strptime(to_time_str, '%I:%M %p').time()
            
            if to_time <= from_time:
                raise serializers.ValidationError("The 'to_time' must be after the 'from_time'.")
        
        return data
        

