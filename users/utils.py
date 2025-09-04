from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode





def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    current_site = get_current_site(request)
    # TODO: use reverse()
    verification_link = f"http://{current_site.domain}/accounts/verify/{uid}/{token}"

    email_subject = "Verify Your Email Address"
    email_body = render_to_string(
        "accounts/verification_email.html",
        {"user": user, "verification_link": verification_link},
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()



from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from .models import Appointments, Services, User_avalablity, User_unavailability


from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from .models import Appointments, Services, User_avalablity, User_unavailability


def validate_appointment_creation(request_data, service_provider):
    """
    Performs all necessary validations for creating a new appointment.

    Args:
        request_data (dict): The data submitted in the request.
        service_provider (User): The user object of the service provider.

    Returns:
        Response or None: A DRF Response object if validation fails, otherwise None.
    """
    # Check service provider status
    if service_provider.status != 'ACTIVE':
        return Response(
            {"detail": "You cannot add appointments while your account status is 'HOLD'. Please contact the admin for assistance."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check appointment limits based on subscription
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    subscription_status = getattr(service_provider, 'subscription_status', None)
    
    appointment_limit = 0
    if subscription_status == 'Monthly':
        appointment_limit = 100
    elif subscription_status == 'Quarterly':
        appointment_limit = 150
    elif subscription_status == 'Yearly':
        appointment_limit = 600
    
    if appointment_limit > 0:
        appointment_count = Appointments.objects.filter(
            service__user=service_provider,
            created_at__gte=current_month_start
        ).count()
        
        if appointment_count >= appointment_limit:
            return Response(
                {"detail": f"Your package has a limit of {appointment_limit} appointments. Please upgrade your package to add more."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Validate time format and create datetime objects
    requested_date = request_data['date']
    requested_time_str = request_data['time']
    try:
        requested_time = datetime.strptime(requested_time_str, '%I:%M %p').time()
        requested_datetime = datetime.combine(requested_date, requested_time)
    except ValueError:
        return Response({"time": "Invalid time format. Please use 'hh:mm AM/PM' (e.g., '02:30 PM')."}, status=status.HTTP_400_BAD_REQUEST)

    # Get user availability data
    try:
        user_availability = User_avalablity.objects.get(user=service_provider)
        available_days = user_availability.days
        appointment_duration = user_availability.time_slot_duration
    except User_avalablity.DoesNotExist:
        # Default values if availability is not set
        appointment_duration = 30
        available_days = []
    
    # Check if the requested day is one of the user's available days
    requested_day_name = requested_date.strftime('%A')
    if requested_day_name not in available_days:
        return Response(
            {"detail": f"Appointments cannot be scheduled on {requested_day_name}. The user is only available on {', '.join(available_days)}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Calculate end datetime
    requested_end_datetime = requested_datetime + timedelta(minutes=appointment_duration)

    # Check for user unavailability periods
    unavailability_periods = User_unavailability.objects.filter(
        user=service_provider,
        from_date__lte=requested_date,
        to_date__gte=requested_date
    )
    for period in unavailability_periods:
        try:
            unavailability_start = datetime.combine(period.from_date, datetime.strptime(period.from_time, '%I:%M %p').time())
            unavailability_end = datetime.combine(period.to_date, datetime.strptime(period.to_time, '%I:%M %p').time())
        except ValueError:
            continue
            
        if (requested_datetime < unavailability_end) and (requested_end_datetime > unavailability_start):
            return Response(
                {"detail": f"User is unavailable from {unavailability_start.strftime('%Y-%m-%d %I:%M %p')} to {unavailability_end.strftime('%Y-%m-%d %I:%M %p')}."},
                status=status.HTTP_400_BAD_REQUEST
            )
   
    # Check for overlapping existing appointments
    existing_appointments = Appointments.objects.filter(
        service__user=service_provider,
        date=requested_date,
        status='ACTIVE'
    )
    for existing_appointment in existing_appointments:
        try:
            existing_availability = User_avalablity.objects.get(user=service_provider)
            existing_duration = existing_availability.time_slot_duration
        except User_avalablity.DoesNotExist:
            existing_duration = 30

        existing_start_time = datetime.combine(existing_appointment.date, datetime.strptime(existing_appointment.time, '%I:%M %p').time())
        existing_end_time = existing_start_time + timedelta(minutes=existing_duration)
        
        if (requested_datetime < existing_end_time) and (requested_end_datetime > existing_start_time):
            return Response({"detail": "This time slot overlaps with an existing appointment."}, status=status.HTTP_400_BAD_REQUEST)
            
    return None