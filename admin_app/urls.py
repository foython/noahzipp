from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrivacyPolicyViewSet, FAQViewSet, get_user_statistics, admin_notification_view

router = DefaultRouter()
router.register(r'privacy-policy', PrivacyPolicyViewSet)
router.register(r'faq', FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user_statistics/', get_user_statistics, name='user_statictis'),
    path('admin_notification/', admin_notification_view, name='user_statictis'),
    path('admin_notification/<int:pk>/', admin_notification_view, name='user_statictis'),
]
