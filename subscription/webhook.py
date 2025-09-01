import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from accounts.models import CustomUser
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

stripe.api_key = "sk_test_51ReHLiH6fkQlm6OO9pBJsy4A9TH9aHZqNjm6dXdz3Rka4tw4VI5p4AuS0rOMUit8XJNPP9DKPiYalfXneCfVg8F300P8KRrKOi"
STRIPE_WEBHOOK_SECRET = 'whsec_Nbir3k2DtSEwuZcjk3LTi1t2PQQ8SbGa'


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body    
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_Nbir3k2DtSEwuZcjk3LTi1t2PQQ8SbGa'                       

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event based on the type
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        subscription_id = session.get('subscription')
        # Retrieve user_id from metadata
        user_id = session['metadata']['user_id']
        package = session['metadata']['package']
        metadata = {"user_id": user_id, "package": package}
        subscription = stripe.Subscription.retrieve(subscription_id)
        updated_subscription = stripe.Subscription.modify(subscription.id, metadata=metadata)
        # Handle the subscription logic for the first-time subscription
        handle_subscription_started(user_id, package, subscription_id)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        subscription_id =  invoice.get('subscription')
        subscription = stripe.Subscription.retrieve(subscription_id)
        metadata = subscription.get('metadata', {})
        user_id = metadata.get('user_id')
        package = metadata.get('package')
        
        handle_subscription_renewal(user_id,package, subscription_id)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        # Retrieve user_id from metadata
        user_id = invoice['metadata']['user_id']
        package = invoice['metadata']['package']
        # Handle the case when payment fails
        handle_failed_payment(user_id, package)

    return JsonResponse({'status': 'success'}, status=200)



def handle_subscription_started(user_id, package, subscription_id):
    try:
        # Corrected line: query CustomUser directly using the primary key (pk)
        user_profile = CustomUser.objects.get(pk=user_id)

        if package == "monthly":
            user_profile.subsciption_expires_on = timezone.now() + timedelta(days=30)
            user_profile.subscription_status = "Monthly"
        else:
            user_profile.subsciption_expires_on = timezone.now() + timedelta(days=365)
            user_profile.subscription_status = "Yearly"
        
        user_profile.is_subscribed = True
        user_profile.subscription_id = subscription_id
        # is_expired field seems to be a custom field not in the provided model.
        # If it's a field you've added, ensure its name is correct.
        # Otherwise, remove this line to prevent errors.
        # user_profile.is_expired = False 
        user_profile.save()

        print(f"Subscription activated for user {user_id}.")

    except CustomUser.DoesNotExist:
        print(f"No user found with user_id {user_id}.")


def handle_subscription_renewal(user_id, package, subscription_id):
    try:
        # Corrected line: query CustomUser directly using the primary key (pk)
        user_profile = CustomUser.objects.get(pk=user_id)
        user_profile.subscription_status = 'subscribed'
        
        if package == "monthly":
            user_profile.subsciption_expires_on = timezone.now() + timedelta(days=30)
            user_profile.subscription_status = "Monthly"
        else:
            user_profile.subsciption_expires_on = timezone.now() + timedelta(days=365)
            user_profile.subscription_status = "Yearly"

        user_profile.is_subscribed = True
        
        user_profile.subscription_id = subscription_id
        # Same as above, ensure this field exists or remove the line.
        # user_profile.is_expired = False 
        user_profile.save()

        print(f"Subscription renewed for user {user_id}.")

    except CustomUser.DoesNotExist:
        print(f"No user found with user_id {user_id}.")


def handle_failed_payment(user_id):
    try:
        # Corrected line: query CustomUser directly using the primary key (pk)
        user_profile = CustomUser.objects.get(pk=user_id)

        # Mark subscription as expired or suspended
        user_profile.subscription_status = 'not_subscribed'
        # Same as above, ensure this field exists or remove the line.
        # user_profile.is_expired = True 
        # The package_name field doesn't exist in your model.
        # You should either remove this line or add the field to your model.
        # user_profile.package_name = "None"
        user_profile.save()

        print(f"Payment failed for user {user_id}, subscription suspended.")

    except CustomUser.DoesNotExist:
        print(f"No user found with user_id {user_id}.")

# @csrf_exempt
# @require_http_methods(["POST"])
# def stripe_webhook(request):
#     payload = request.body
#     print(payload)
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     endpoint_secret = 'whsec_e56f55d5d4030083286ec876776cde4540c98e535821a4b9d50e35a2cfff3798'                       

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)

#     # Handle the event based on the type
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         subscription_id = session.get('subscription')
#         # Retrieve user_id from metadata
#         user_id = session['metadata']['user_id']
#         package = session['metadata']['package']
#         metadata = {"user_id": user_id, "package": package}
#         subscription = stripe.Subscription.retrieve(subscription_id)
#         updated_subscription = stripe.Subscription.modify(subscription.id, metadata=metadata)
#         # Handle the subscription logic for the first-time subscription
#         handle_subscription_started(user_id, package, subscription_id)

#     elif event['type'] == 'invoice.payment_succeeded':
#         invoice = event['data']['object']
#         subscription_id =  invoice.get('subscription')
#         subscription = stripe.Subscription.retrieve(subscription_id)
#         metadata = subscription.get('metadata', {})
#         user_id = metadata.get('user_id')
#         package = metadata.get('package')
        
#         handle_subscription_renewal(user_id,package, subscription_id)

#     elif event['type'] == 'invoice.payment_failed':
#         invoice = event['data']['object']
#         # Retrieve user_id from metadata
#         user_id = invoice['metadata']['user_id']
#         package = invoice['metadata']['package']
#         # Handle the case when payment fails
#         handle_failed_payment(user_id, package)

#     return JsonResponse({'status': 'success'}, status=200)


# def handle_subscription_started(user_id, package, subscription_id):
#     try:
#         user_profile = CustomUser.objects.get(user=User.objects.get(pk=user_id))

#         if package == "monthly":
#             user_profile.subsciption_expires_on = timezone.now() + timedelta(days=30)
#             user_profile.subscription_status = "Monthly"
#         else:
#             user_profile.subsciption_expires_on = timezone.now() + timedelta(days=365)
#             user_profile.subscription_status = "Yearly"
        
#         user_profile.is_subscribed = True
#         user_profile.subscription_id = subscription_id
#         user_profile.is_expired = False
#         user_profile.save()

#         print(f"Subscription activated for user {user_id}.")

#     except user_profile.DoesNotExist:
#         print(f"No user found with user_id {user_id}.")


# def handle_subscription_renewal(user_id, package, subscription_id):
#     try:
#         user_profile = CustomUser.objects.get(user=User.objects.get(pk=user_id))
#         user_profile.subscription_status = 'subscribed'
        
#         if package == "monthly":
#             user_profile.subsciption_expires_on = timezone.now() + timedelta(days=30)
#             user_profile.subscription_status = "Monthly"
#         else:
#             user_profile.subsciption_expires_on = timezone.now() + timedelta(days=365)
#             user_profile.subscription_status = "Yearly"

#         user_profile.is_subscribed = True
        
#         user_profile.subscription_id = subscription_id
#         user_profile.is_expired = False
#         user_profile.save()

#         print(f"Subscription renewed for user {user_id}.")

#     except CustomUser.DoesNotExist:
#         print(f"No user found with user_id {user_id}.")


# def handle_failed_payment(user_id):
#     try:
#         # Fetch user profile based on user_id
#         user_profile = CustomUser.objects.get(user=User.objects.get(pk=user_id))

#         # Mark subscription as expired or suspended
#         user_profile.subscription_status = 'not_subscribed'
#         user_profile.is_expired = True
#         user_profile.package_name = "None"
#         user_profile.save()

#         print(f"Payment failed for user {user_id}, subscription suspended.")

#     except CustomUser.DoesNotExist:
#         print(f"No user found with user_id {user_id}.")