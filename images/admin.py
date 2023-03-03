from django.contrib import admin

from .models import PhotoAlbum

class PhotoAlbumAdmin(admin.ModelAdmin):

    list_display = ['id', 'is_active', 'disabled', 'is_profile', 'artist', 'image']

admin.site.register(PhotoAlbum, PhotoAlbumAdmin)