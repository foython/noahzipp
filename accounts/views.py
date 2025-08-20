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
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.core import signing


# Create your views here.
User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
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
    user = User.objects.filter(username=email).first()
    if user.is_varified == False:
        return Response(
            {
                "Message": "Please verify your OTP first."
            },
            status=400
        )

    if User.objects.filter(username=email).count() > 0:
        return Response(
            {
                "Message": "The email is already registered."
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def normal_login(request):
    email = request.data.get('email')
    password = request.data.get('password')    

    if not email or not password:
        return Response({"Message": "Both Username and password are required."}, status=400)
    
    # Use the email as the username for authentication
    user = authenticate(username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            # Corrected line: Pass the user object directly to the serializer
            'user_profile': CustomUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({"Message": "Invalid credentials."}, status=401)
    

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
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email(request):
    old_email = request.data.get('old_email', None)
    new_email = request.data.get('new_email', None)
    
    if not old_email or not new_email:
        return Response(
            {"message": "Both old and new email addresses are required."},
            status=400
        )

    user = request.user
    
    if user.email != old_email:
        return Response(
            {"message": "The provided old email does not match your current email."},
            status=400
        )
   
    if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
        return Response(
            {"message": "This new email is already in use by another user."},
            status=400
        )

    
    try:
        user.email = new_email
        user.username = new_email # Recommended to keep username and email in sync
        user.save()
        
        return Response(
            {"message": "Email address updated successfully."},
            status=200
        )
    except Exception as e:
        return Response(
            {"message": f"An unexpected error occurred: {str(e)}"},
            status=500
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    

    # 1. Check if all fields are provided
    if not old_password or not new_password:
        return Response(
            {"message": "All fields are required: old_password and new_password."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    # 3. Check if the old password is correct
    if not user.check_password(old_password):
        return Response(
            {"message": "Incorrect old password."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. Set the new password
    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password changed successfully."},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def forget_password(request):
    email = request.data.get('email')
    if not email:
        return Response(
            {"Message": "Email address is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"Message": "Email not found."},
                status=status.HTTP_404_NOT_FOUND
            )
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
    except Exception as e:
        return Response(
            {"Message": "Something went wrong.", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
TOKEN_EXPIRY_MINUTES = 15

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verify_otp(request):
    otp = request.data.get('otp')
    email = request.data.get('email')

    try:
        user = User.objects.get(username=email)

        if user.otp != otp:
            return Response({"Message": "Invalid OTP"}, status=400)

        if user.updated_at < timezone.now() - timedelta(minutes=10):
            return Response({"Message": "OTP expired"}, status=400)

        # Generate signed token
        payload = {
            "email": user.email,
            "ts": timezone.now().timestamp()
        }
        token = signing.dumps(payload, salt="reset-password")

        return Response(
            {
                "Message": "OTP verified successfully.",
                "reset_token": token
            },
            status=200
        )

    except User.DoesNotExist:
        return Response({"Message": "No account found with that email."}, status=400)
    


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_change(request):
    token = request.data.get("reset_token")
    new_password = request.data.get("password")

    try:
        # Verify signed token
        data = signing.loads(token, salt="reset-password", max_age=TOKEN_EXPIRY_MINUTES * 60)
        email = data.get("email")

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.otp = None
        user.save()

        return Response({"Message": "Password updated successfully."}, status=200)

    except signing.SignatureExpired:
        return Response({"Message": "Reset token expired."}, status=400)
    except signing.BadSignature:
        return Response({"Message": "Invalid reset token."}, status=400)
    except Exception:
        return Response({"Message": "Something went wrong."}, status=500)



@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
   
    try:
        user = request.user
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':        
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    serializer = CustomUserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')
    
    if not email:
        return Response(
            {"Message": "Email address is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Corrected: Get the user object by email (or username)
        user = User.objects.get(email=email) # Using email field is more direct

        # Corrected: Call generate_otp directly on the user object you just retrieved
        otp = user.generate_otp()
        
        subject = 'Here is your verification code'
        message = f'Hello, you have requested an OTP for verification, here is your otp: {otp}'
        from_email = 'pialzoad@gmail.com'
        recipient_list = [email]

        email_message = EmailMessage(subject, message, from_email, recipient_list)
        email_message.send()

        return Response(
            {
                "Message": "Successfully Resent OTP."
            },
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        # This catches the specific case where no user is found
        return Response(
            {
                "Message": "No account found with the given email address."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        # Catch other unexpected errors (e.g., email sending failure)
        print(f"An unexpected error occurred: {e}")
        return Response(
            {
                "Message": "An unexpected error occurred. Please try again."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )