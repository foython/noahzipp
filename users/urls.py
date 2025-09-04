from django.urls import path
from .views import manage_chatbots, manage_services, create_appointment_view, monthly_appointments_api_view, appointment_summary_api_view, manage_discounts, user_availability_view, set_unavailability_view, user_notification_view, chatbot_id, recent_appointments, cancel_appointment_status, reschedule_appointment_status

urlpatterns = [
    # Chatbot URLs
    path('chatbots/', manage_chatbots, name='chatbot-list'),
    path('chatbots/<int:pk>/', manage_chatbots, name='chatbot-detail'),
    path('chatbots_id/', chatbot_id, name='chatbot-id'),
    
    # Services URLs
    path('services/', manage_services, name='service-list'),
    path('services/<int:pk>/', manage_services, name='service-detail'),
    path('services/discounts/', manage_discounts, name='manage_discounts_list_create'),
    path('services/discounts/<int:pk>/', manage_discounts, name='manage_discounts_by_id'),
    
    # Appointments URLs
    path('appointments/', create_appointment_view, name='appointment-list'),
    path('appointments/<int:pk>/', create_appointment_view, name='appointment-detail'),
    path('chatbots_appointments/chart/data/', monthly_appointments_api_view, name='appointment-chart-data'),
    path('cancel_appointments_status/<int:pk>/', cancel_appointment_status, name='cancel_appointment'),
    path('reschedule_appointments_status/<int:pk>/', reschedule_appointment_status, name='reschedule_appointment'),
    path('appointments_summary/', appointment_summary_api_view, name='appointments_summary_api'),
    path('availability/', user_availability_view, name='user_availability_api'),
    path('set-unavailability/<int:pk>/', set_unavailability_view, name='unavailability-detail'),
    path('set-unavailability/', set_unavailability_view, name='set-unavailability'),
    path('notifications/', user_notification_view, name='user-notifications-list'),
    path('recent_apinments/', recent_appointments, name='recent_apinments-list'),

]
reschedule_appointment_status