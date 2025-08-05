from django.shortcuts import render
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser


# Create your views here.
User = get_user_model()

@api_view(['POST'])
def normal_register(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)

    if email is None or password is None:
        return Response(
            {
                "Message": "Both Email and Passwords are required."
            },
            status=400
        )

    if User.objects.filter(username=email).count() > 0:
        return Response(
            {
                "Message": "The email is already used by another user."
            },
            status=400
        )
    
    user = User()
    user.username = email
    user.email = email
    user.set_password(password)
    user.save()

    otp = user.generate_otp()

    subject = 'Here is your verification code'
    message = f'Hello, please verify your account with the OTP: {otp}'
    from_email = 'support@gameplanai.co.uk'
    recipient_list = [email]

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.send()
 
    return Response( {
            
            
            'message': 'OTP Sent Successfully.'
        }, 
        status=201
    )


@api_view(['POST'])
def verify_otp(request):
    otp = request.data.get('otp')
    email = request.data.get('email')

    try:
        user = User.objects.get(username=email)
        
        if user.otp == otp:
            user.is_varified = True
            user.save()
            return Response(
                {
                    "Message": "Successfully verified your OTP."
                },
                status=200
            )
        else:
            return Response(
                {
                    "Message": "Invalid OTP, please try again."
                },
                status=400
            )
    except Exception as e:
        print(e)
        return Response(
            {
                "Message": "No account found with that email address."
            },
            status=400
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=205)
    except Exception as e:
        return Response({"detail": "Invalid token or token already blacklisted."}, status=400)
    



class UserProfileViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class= CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):        
        user = self.request.user
        if user.role == 'ADMIN': 
            return CustomUser.objects.all()
        return CustomUser.objects.filter(pk=user.pk)