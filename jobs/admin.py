from django.contrib import admin

from .models import Category, ArtistProfile, Solicitation, SolicitationInvite

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Categoria', {'fields': ['name', 'image', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class ArtistProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Profile', {'fields': ['name', 'age', 'age_max', 'hair', 'eye', 'skin', 'stature', 'stature_max', 'waist', 'waist_max',
                                'hip', 'hip_max', 'bust', 'bust_max', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class SolicitationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Profile', {'fields': ['status', 'client', 'approved', 'profile', 'title', 'category', 'description', 'time', 'address_street',
                                'address_neighborhood', 'address_number', 'address_city', 'address_state', 'address_complement', 'full_address',
                                'date', 'value', 'transport', 'feeding', 'campaign_broadcast', 'image_right_time', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'category', 'client', 'status']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class SolicitationInviteAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Convite', {'fields': ['client_evaluated', 'artist_evaluated', 'job', 'artist', 'artist_status', 'client_status', 'notification_send', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'job', 'artist', 'artist_status', 'client_status']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

admin.site.register(Category, CategoryAdmin)
admin.site.register(ArtistProfile, ArtistProfileAdmin)
admin.site.register(Solicitation, SolicitationAdmin)
admin.site.register(SolicitationInvite, SolicitationInviteAdmin)