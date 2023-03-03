from rest_framework import routers

from django.urls import path, include

from .views import ClassManagementViewSet 

router = routers.SimpleRouter()

router.register('v1/video/class', ClassManagementViewSet)

urlpatterns = router.urls

