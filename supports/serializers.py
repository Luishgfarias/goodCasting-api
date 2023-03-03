from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist
from django.core.files.base import ContentFile
from .models import ContactForm
from .models import Notification

class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = ['id', 'name', 'email', 'title', 'message', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Notification
    fields = '__all__'
