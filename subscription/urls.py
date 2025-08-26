from django.urls import path
from . import views
from .webhook import stripe_webhook

urlpatterns = [
    path('buy_subscription/', views.buy_subscription_on_app, name='buy_subscription_on_app'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('webhook/', stripe_webhook, name='stripe_webhook')
]