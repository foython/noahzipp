from django.contrib import admin
from .models import (
    Chatbot, 
    Services, 
    service_discount, 
    Appointments, 
    User_avalablity,
    User_unavailability,
    user_notification
   
)

# Admin class for the Chatbot model
@admin.register(Chatbot)
class ChatbotAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'chatting_style', 'description')
    search_fields = ('name', 'owner__username')
    list_filter = ('chatting_style',)
    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'chatting_style', 'description', 'logo')
        }),
    )

# Admin class for the Services model
@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'user', 'price', 'status')
    search_fields = ('service_name', 'user__username')
    list_filter = ('status',)
    fieldsets = (
        (None, {
            'fields': ('user', 'service_name', 'Description_of_service', 'price', 'status')
        }),
    )

# Admin class for the service_discount model
@admin.register(service_discount)
class ServiceDiscountAdmin(admin.ModelAdmin):
    list_display = ('service', 'discount_price', 'discount_deadline', 'status')
    search_fields = ('service__service_name',)
    list_filter = ('status',)
    fieldsets = (
        (None, {
            'fields': ('service', 'discount_price', 'discount_deadline', 'status')
        }),
    )


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):    
    search_fields = ('customer', 'contact')
    list_filter = ('status', 'date')
   
    

admin.site.register(User_avalablity)
admin.site.register(User_unavailability)
admin.site.register(user_notification)