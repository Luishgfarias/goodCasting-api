from django.contrib import admin

from .models import ContactForm

class ContactFormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Contato', {'fields': ['name', 'email', 'title', 'message', 'created_at', 'updated_at']})
    ]

    readonly_fields = ['created_at', 'updated_at']
    list_display = ['id', 'title']
    list_per_page = 30

admin.site.register(ContactForm, ContactFormAdmin)
from .models import Notification

# Register your models here.

class NotificationAdmin(admin.ModelAdmin):
  list_display = ['id', 'title', 'message', 'visible', 'artist', 'client']
  pass

admin.site.register(Notification, NotificationAdmin)
