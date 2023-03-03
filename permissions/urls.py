from rest_framework import routers

from django.urls import path, include

from .views import PermissionViewSet, UserTypeViewSet 

router = routers.SimpleRouter()

router.register('v1/permission/list', PermissionViewSet)
router.register('v1/permission/type', UserTypeViewSet)


urlpatterns = router.urls

