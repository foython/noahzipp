from django.urls import path
from .views import manage_chatbots, manage_services, create_appointment_view, monthly_appointments_api_view, appointment_summary_api_view, manage_discounts, user_availability_view

urlpatterns = [
    # Chatbot URLs
    path('chatbots/', manage_chatbots, name='chatbot-list'),
    path('chatbots/<int:pk>/', manage_chatbots, name='chatbot-detail'),
    
    # Services URLs
    path('services/', manage_services, name='service-list'),
    path('services/<int:pk>/', manage_services, name='service-detail'),
    path('services/discounts/', manage_discounts, name='manage_discounts_list_create'),
    path('services/discounts/<int:pk>/', manage_discounts, name='manage_discounts_by_id'),
    
    # Appointments URLs
    path('appointments/', create_appointment_view, name='appointment-list'),
    # path('chatbots_appointments/<int:pk>/', manage_appointments, name='appointment-detail'),
    path('chatbots_appointments/chart/data/', monthly_appointments_api_view, name='appointment-chart-data'), 
    path('appointments_summary/', appointment_summary_api_view, name='appointments_summary_api'),
    path('availability/', user_availability_view, name='user_availability_api'),

]
