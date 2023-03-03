from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import PhotoAlbum
from django.db.models.base import ObjectDoesNotExist
from middlewares.middlewares import RequestMiddleware


class PhotoAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoAlbum
        fields = ['id', 'is_active', 'is_profile', 'artist', 'image', 'created_at', 'updated_at', 'disabled']

    # def to_representation(self, instance):
    #     custom_request = RequestMiddleware(get_response=None)
    #     custom_request = custom_request.thread_local.current_request
    #     url_image = 'https://' + custom_request.META['HTTP_HOST']
        
    #     response = super().to_representation(instance)
    #     response['image'] = '' if instance.image == "" or instance.image == None else url_image + instance.image.url
    #     return response