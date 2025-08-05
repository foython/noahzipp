# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'role', 'gender', 'profession',
            'date_of_birth', 'profile_picture', 'phone_number', 'location', 'country',
            'time_zone', 'upload_logo', 'about_yourself', 'professional_background'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)



class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
