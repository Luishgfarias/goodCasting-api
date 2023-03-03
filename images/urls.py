from rest_framework import routers

from django.urls import path, include

from .views import PhotoAlbumViewSet

router = routers.SimpleRouter()

router.register('v1/image/photo', PhotoAlbumViewSet)

urlpatterns = router.urls

