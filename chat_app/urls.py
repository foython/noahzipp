from django.urls import path
from . import views
 
urlpatterns = [
    path('chat/<int:unique_id>/', views.send_message, name='chat_message'),
    path('embed/', views.get_embedding, name='get_embed_code'),
    path('dashboard-chat/', views.chatbot_for_website, name='dashboard_chatbot'),
]