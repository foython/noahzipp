from rest_framework import serializers
from .models import PrivacyPolicy, FAQ, AdminNotification

class PrivacyPolicySerializer(serializers.ModelSerializer):

    class Meta:       
        model = PrivacyPolicy        
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
   
    class Meta:        
        model = FAQ        
        fields = '__all__'


class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = '__all__'