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
    Description_of_service = models.TextField()
    customer = models.CharField(max_length=128)
    contact = models.CharField(max_length=36)
    date = models.DateField()   
    
    time = models.CharField(max_length=8, validators=[time_validator])
    
    about = models.TextField()
    status = models.CharField(max_length=28, choices=STATUS, default='ACTIVE')   

    def __str__(self):
        return self.customer + ' - ' + str(self.date) + ' ' + str(self.time)



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