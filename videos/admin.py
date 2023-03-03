from django.contrib import admin

from .models import ClassManagement

class ClassManagementAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'subtitle', 'title', 'link', 'order', 'description']

admin.site.register(ClassManagement, ClassManagementAdmin)