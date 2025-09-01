from rest_framework import serializers
from .models import Chatbot, Services, Appointments, service_discount, User_avalablity, User_unavailability, time_validator, user_notification
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
            'customer_name', 
            'contact_number', 
            'customer_email',
            'service_description', 
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
        

class UserUnavailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for the User_unavailability model.
    """
    from_time = serializers.CharField(max_length=8, validators=[time_validator])
    to_time = serializers.CharField(max_length=8, validators=[time_validator])

    class Meta:
        model = User_unavailability
        fields = ['id', 'reason', 'from_date', 'from_time', 'to_date', 'to_time']
        read_only_fields = ['user']

    def validate(self, data):
        """
        Validates that the 'to' datetime is after the 'from' datetime.
        """
        from_date = data.get('from_date')
        from_time_str = data.get('from_time')
        to_date = data.get('to_date')
        to_time_str = data.get('to_time')
        
        try:
            from_time = datetime.strptime(from_time_str, '%I:%M %p').time()
            to_time = datetime.strptime(to_time_str, '%I:%M %p').time()
        except ValueError:
            raise serializers.ValidationError("Time format is invalid. Use 'hh:mm AM/PM'.")

        from_datetime = datetime.combine(from_date, from_time)
        to_datetime = datetime.combine(to_date, to_time)

        if to_datetime <= from_datetime:
            raise serializers.ValidationError("The 'to' date and time must be after the 'from' date and time.")
        
        return data


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_notification
        fields = ['id', 'user', 'message', 'is_read']
        read_only_fields = ['user', 'message']
