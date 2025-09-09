from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from accounts.serializers import CustomUserSerializer
from accounts.models import CustomUser
from django.conf import settings
from django.http import JsonResponse
import os, json
from dotenv import load_dotenv 
load_dotenv()
CustomUser = get_user_model()

import stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")



prices = {
    'monthly': 'price_1Rea3gH6fkQlm6OOM9jVmv5l',
    'yearly': 'price_1ReyseH6fkQlm6OO9fqreTdq'
}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_subscription_on_app(request):
    import traceback

    user = request.user
    subscription_plan = request.data.get('subscription_plan')
    success_url = request.data.get('success_url')
    cancel_url = request.data.get('cancel_url')

    if subscription_plan not in prices:
        return JsonResponse({'error': 'Invalid subscription plan'}, status=400)

    # Check for missing URLs in the payload
    if not success_url or not cancel_url:
        return JsonResponse({'error': 'Missing success_url or cancel_url in payload'}, status=400)

    if user.is_subscribed:
        return Response({"Message": "You are already subscribed! Please cancel your existing subscription if you wish to update it."}, status=status.HTTP_200_OK)
    
    if user.subscription_status == "cancelled":
        return Response({"Message": "You already cancelled your subscription! Please wait until your current billing period ends."}, status=status.HTTP_200_OK)

    try:
        price_id = prices[subscription_plan]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,  # Use the URL from the payload
            cancel_url=cancel_url,    # Use the URL from the payload
            metadata={'user_id': str(user.pk), 'package': subscription_plan},
        )

        print("Checkout session:", checkout_session)

        return JsonResponse({'checkout_url': checkout_session.url})

    except Exception as e:
        print("Exception during Stripe session creation:", str(e))
        traceback.print_exc()
        return JsonResponse({'error': 'Failed to create Stripe checkout session'}, status=500)


@api_view(['GET'])
def success(request):
    return Response({"Message": "Success"}, status=status.HTTP_200_OK)



@api_view(['GET'])
def cancel(request):
    return Response({"Message": "Cancel"}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    user_profile = CustomUser.objects.get(user=user)
    subscription_id = user_profile.subscription_id
    try:
        canceled_subscription = stripe.Subscription.delete(subscription_id)
        user_profile.subscription_status = "cancelled"
        user_profile.save()
        return Response({"Message": "Subscription Cancelled Successfully."}, status=status.HTTP_200_OK)
    except:
        return Response({"Message": "Subscription Already Cancelled."}, status=status.HTTP_200_OK)




class IsAdminUser(BasePermission):
   
    def has_permission(self, request, view):
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True        
       
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
    

class SubscriptionPlanView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            plan = get_object_or_404(SubscriptionPlan, pk=pk)
            serializer = SubscriptionPlanSerializer(plan)
        else:
            plans = SubscriptionPlan.objects.all()
            serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_BAD_REQUEST)

    def patch(self, request, pk=None):
        plan = get_object_or_404(SubscriptionPlan, pk=pk)
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk=None):
        plan = get_object_or_404(SubscriptionPlan, pk=pk)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'PATCH'])
def subscribe_user_view(request, pk=None):
    
    if request.user.role != 'ADMIN':
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if pk:
            try:
                user = CustomUser.objects.get(pk=pk)
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Subscribed user not found."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            subscribed_users = CustomUser.objects.filter(is_subscribed=True)
            serializer = CustomUserSerializer(subscribed_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        if request.user.role != 'ADMIN':
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        
        if not pk:
            return Response({"detail": "User ID is required in the URL to update."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_update = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)
        
        # Check if a 'status' change is requested
        if 'status' in request.data:
            new_status = request.data.get('status')
            valid_statuses = [s[0] for s in CustomUser.STATUS]
            
            if new_status not in valid_statuses:
                return Response(
                    {"detail": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_to_update.status = new_status
            user_to_update.save()
            
            serializer = CustomUserSerializer(user_to_update)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Check for subscription status update
        subscription_status = request.data.get('subscription_status')
        
        if subscription_status:
            if user_to_update.is_subscribed and user_to_update.subscription_status == subscription_status:
                return Response({"detail": "User is already subscribed."},
                                status=status.HTTP_409_CONFLICT)
            
            valid_packages = ['MONTHLY', 'QUARTERLY', 'HALF YEARLY', 'YEARLY']
            if subscription_status not in valid_packages:
                return Response(
                    {"detail": "Invalid subscription status. Must be one of: " + ", ".join(valid_packages)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_to_update.subscription_status = subscription_status
            user_to_update.is_subscribed = True
           
            if subscription_status == 'MONTHLY':
                user_to_update.subsciption_expires_on = datetime.now() + timedelta(days=30)
            elif subscription_status == 'QUARTERLY':
                user_to_update.subsciption_expires_on = datetime.now() + timedelta(days=90)
            elif subscription_status == 'HALF YEARLY':
                user_to_update.subsciption_expires_on = datetime.now() + timedelta(days=180)
            elif subscription_status == 'YEARLY':
                user_to_update.subsciption_expires_on = datetime.now() + timedelta(days=365)
            
            user_to_update.save()
            
            serializer = CustomUserSerializer(user_to_update)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Handle cases where neither status nor subscription_status is provided
        return Response(
            {"detail": "The 'subscription_status' or 'status' field is required to update data."},
            status=status.HTTP_400_BAD_REQUEST
        )
        

@api_view(['GET'])
def non_subscribe_user_view(request, pk=None):
    
    if request.user.role != 'ADMIN':
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if pk:
            try:
                user = CustomUser.objects.get(pk=pk, is_subscribed=False)
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Nonsubscribed user not found."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            subscribed_users = CustomUser.objects.filter(is_subscribed=False)
            serializer = CustomUserSerializer(subscribed_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_subscription_by_pk(request, pk):
      
    try:     
        user_profile = CustomUser.objects.get(pk=pk)

        if user_profile.is_subscribed == True:                              
      
            user_profile.subscription_status = "cancelled"
            user_profile.is_subscribed = False
            user_profile.subsciption_expires_on = None
            user_profile.save()

            return Response(
                {"Message": "Subscription Deleted Successfully."},
                status=status.HTTP_200_OK
            )
    except CustomUser.DoesNotExist:

        return Response(
            {"Message": "User profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except stripe.error.StripeError as e:
    
        return Response(
            {"Message": f"Stripe error: {e.user_message}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"Message": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
