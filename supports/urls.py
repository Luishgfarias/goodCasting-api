from rest_framework import routers

from django.urls import path, include

from .views import ContactFormViewSet, NotificationViewSet

router = routers.SimpleRouter()

router.register('v1/support/contact', ContactFormViewSet)

router.register('v1/support/notification', NotificationViewSet)

urlpatterns = router.urls

