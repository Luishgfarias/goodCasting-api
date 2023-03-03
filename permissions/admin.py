from django.contrib import admin

from .models import Permission, UserType

class PermissionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Permissão', {'fields': ['function', 'model', 'active', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'function', 'model']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class UserTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Tipo de Usuário', {'fields': ['name', 'permission', 'active', 'is_superuser', 'is_staff', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30


admin.site.register(Permission, PermissionAdmin)
admin.site.register(UserType, UserTypeAdmin)