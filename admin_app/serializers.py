from rest_framework import serializers
from .models import PrivacyPolicy, FAQ

class PrivacyPolicySerializer(serializers.ModelSerializer):

    class Meta:       
        model = PrivacyPolicy        
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
   
    class Meta:        
        model = FAQ        
        fields = '__all__'
