from django.db import models
from accounts.models import TimeStamp, CustomUser

# Create your models here.


class PrivacyPolicy(TimeStamp):
    privacy_policy = models.TextField()

    

class FAQ(TimeStamp):
    questions_type = models.CharField(max_length=256)
    questions = models.CharField(max_length=512)
    answer = models.TextField()


class AdminNotification(TimeStamp):    
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' - ' + self.message[:20] + ('...' if len(self.message) > 20 else '')
    

class Logo(TimeStamp):
    image = models.ImageField(upload_to='logo/')
    
    def __str__(self):
        return f"Logo {self.id}"