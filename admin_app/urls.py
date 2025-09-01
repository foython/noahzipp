from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrivacyPolicyViewSet, FAQViewSet

router = DefaultRouter()
router.register(r'privacy-policy', PrivacyPolicyViewSet)
router.register(r'faq', FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
