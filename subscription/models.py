from django.db import models
from accounts.models import TimeStamp
# Create your models here.
class SubscriptionPlan(TimeStamp):
    PACKAGE = (
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
        ('HALF YEARLY', 'Half Yearly'),
        ('QUARTERLY', 'Quarterly')
    )
    plan_name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    package_type = models.CharField()
    description = models.TextField()
    features = models.JSONField()

    def __str__(self):
        return self.plan_name