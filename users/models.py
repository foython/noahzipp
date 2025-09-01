from django.db import models
from accounts.models import CustomUser
from accounts.models import TimeStamp
from django.core.validators import RegexValidator
# Create your models here.




class Chatbot(TimeStamp):
    STYLE = (
        ('CASUAL', 'Casual'),
        ('FRIENDLY', 'Friendly'),
        ('PROFESSIONAL', 'Professional'),
    )
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chatbot_owner')
    name = models.CharField(max_length=128, unique=True)
    chatting_style = models.CharField(max_length=128, choices=STYLE, default='CASUAL')
    description = models.TextField(blank=True, null=True)      
    logo = models.ImageField(upload_to='chatbot_logo/', blank=True, null=True)

    def __str__(self):
        return self.name
    


class Services(TimeStamp):
    STATUS = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_owner')
    service_name = models.CharField(max_length=128)
    Description_of_service = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=28, choices=STATUS, default='ACTIVE')   
    

    def __str__(self):
        return self.service_name



class service_discount(TimeStamp):
    STATUS = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='service_discount')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_deadline = models.DateField()
    status = models.CharField(max_length=28, choices=STATUS, default='INACTIVE')

    def __str__(self):
        return self.service.service_name + ' - ' + str(self.discount_price)
    



time_validator = RegexValidator(
    regex=r'(?i)^((0?[1-9]|1[0-2]):[0-5][0-9]\s?(am|pm))$',
    message='Enter a valid time in hh:mm AM/PM format (e.g., 02:30 PM).',
    code='invalid_time'
)

class Appointments(TimeStamp):
    STATUS = (
        ('ACTIVE', 'Active'),
        ('CANCELED', 'Canceled'),
        ('RESCHEDULED', 'Rescheduled'),
    )
    
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='appointments')
    customer_name = models.CharField(max_length=128)    
    contact_number = models.CharField(max_length=36, blank=True)    
    customer_email = models.CharField(max_length=128, blank=True)
    service_description = models.TextField()
    date = models.DateField(blank=True)      
    time = models.CharField(max_length=8, blank=True, validators=[time_validator])    
    about = models.TextField(blank=True)
    status = models.CharField(max_length=28, choices=STATUS, default='ACTIVE')   

    def __str__(self):
        return self.customer_name + ' - ' + str(self.date) + ' ' + str(self.time)



class User_avalablity(TimeStamp):
    
    time_validator = RegexValidator(
        regex=r'(?i)^((0?[1-9]|1[0-2]):[0-5][0-9]\s?(am|pm))$',
        message='Enter a valid time in hh:mm AM/PM format (e.g., 02:30 PM).',
        code='invalid_time'
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_avalablit')   
   
    days = models.JSONField() 
    
    from_time = models.CharField(max_length=8, validators=[time_validator])
    to_time = models.CharField(max_length=8, validators=[time_validator])
    time_slot_duration = models.IntegerField(default=30, help_text="Duration in minutes")
    def __str__(self):
        return self.user.username + ' - ' + ', '.join(self.days)
    

class User_unavailability(TimeStamp):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_unavalablit')
    reason = models.CharField(max_length=128)
    from_date = models.DateField()
    from_time = models.CharField(max_length=8, validators=[time_validator])
    to_date = models.DateField()
    to_time = models.CharField(max_length=8, validators=[time_validator])

    def __str__(self):
        return self.user.username + ' - ' + str(self.from_date) + ' ' + str(self.from_time) + ' to ' + str(self.to_date) + ' ' + str(self.to_time)


class user_notification(TimeStamp):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_notification')
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' - ' + self.message[:20] + ('...' if len(self.message) > 20 else '')
    

