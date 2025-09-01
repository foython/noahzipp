from django.db import models
from accounts.models import TimeStamp
# Create your models here.


class PrivacyPolicy(TimeStamp):
    privacy_policy = models.TextField()

    

class FAQ(TimeStamp):
    questions_type = models.CharField(max_length=256)
    questions = models.CharField(max_length=512)
    answer = models.TextField()