from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist
from django.core.files.base import ContentFile
from .models import ClassManagement
from images import models as image_models

class ClassManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassManagement
        fields = ['id', 'is_active', 'subtitle', 'title', 'link', 'order', 'description', 'created_at', 'updated_at']