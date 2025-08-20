from django.urls import path
from .views import manage_chatbots, manage_services, manage_appointments

urlpatterns = [
    # Chatbot URLs
    path('chatbots/', manage_chatbots, name='chatbot-list'),
    path('chatbots/<int:pk>/', manage_chatbots, name='chatbot-detail'),
    
    # Services URLs
    path('chatbots_services/', manage_services, name='service-list'),
    path('chatbots_services/<int:pk>/', manage_services, name='service-detail'),
    
    # Appointments URLs
    path('chatbots_appointments/', manage_appointments, name='appointment-list'),
    path('chatbots_appointments/<int:pk>/', manage_appointments, name='appointment-detail'),
]
