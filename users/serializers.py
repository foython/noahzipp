from rest_framework import serializers
from .models import Chatbot, Services, Appointments

class ChatbotSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chatbot
        fields = '__all__'
        read_only_fields = ('owner',)

class ServicesSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Services
        fields = '__all__'        
        

class AppointmentsSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Appointments
        fields = '__all__'
