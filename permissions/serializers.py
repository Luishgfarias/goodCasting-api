from rest_framework import serializers

from .models import Permission, UserType

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'model', 'function', 'active', 'created_at', 'updated_at']

class UserTypeSerializer(serializers.ModelSerializer):
    list_permissions = PermissionSerializer(source='permission', many=True, read_only=True)
    class Meta:
        model = UserType
        fields = ['id', 'name', 'permission', 'active', 'is_superuser', 'is_staff', 'created_at', 'updated_at', 'list_permissions']