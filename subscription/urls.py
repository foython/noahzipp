from django.urls import path
from . import views
from .webhook import stripe_webhook

urlpatterns = [
    path('plans/', views.SubscriptionPlanView.as_view()),         
    path('plans/<int:pk>/', views.SubscriptionPlanView.as_view()), 
    path('buy/', views.buy_subscription_on_app, name='buy_subscription_on_app'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('subscribers/', views.subscribe_user_view, name='subscribers_list'),
    path('subscribers/<int:pk>/', views.subscribe_user_view, name='subscribers_patch'),
    path('non-subscribers/', views.non_subscribe_user_view, name='nonsubscribers_list'),
    path('non-subscribers/<int:pk>/', views.non_subscribe_user_view, name='nonsubscribers'),
    path('delete-subscribers/<int:pk>/', views.cancel_subscription_by_pk, name='delete-subscribers'),
]

