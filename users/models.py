from django.db import models
from accounts.models import CustomUser
from accounts.models import TimeStamp
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
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='chatbot_service')
    service_name = models.CharField(max_length=128)
    Description_of_service = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=28, choices=STATUS, default='USER')
    diccount = models.BooleanField(default=False)
    discount_price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    discount_deadline = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.service_name
    



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
    time = models.TimeField()
    about = models.TextField()
    status = models.CharField(max_length=28, choices=STATUS, default='ACTIVE')   

    def __str__(self):
        return self.customer + ' - ' + str(self.date) + ' ' + str(self.time)   