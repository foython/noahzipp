from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrivacyPolicyViewSet, FAQViewSet, get_user_statistics, admin_notification_view, monthly_user_registrations_api_view

router = DefaultRouter()
router.register(r'privacy-policy', PrivacyPolicyViewSet)
router.register(r'faq', FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user_statistics/', get_user_statistics, name='user_statictis'),
    path('user_reg_statistics/', monthly_user_registrations_api_view, name='user_statictis'),
    path('admin_notification/', admin_notification_view, name='admin_notification'),
    path('admin_notification/<int:pk>/', admin_notification_view, name='admin_notification_by _id'),
]
