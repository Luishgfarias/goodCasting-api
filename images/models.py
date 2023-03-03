from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from users import models as user_models

# class ArtistAlbum(models.Model):
#     artist = models.OneToOneField('users.UserArtist', verbose_name='Artista', db_column='artist', blank=False, null=True, on_delete=models.SET_NULL)
#     created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

#     class Meta:
#         db_table = 'artist_album'
#         verbose_name = 'Album'
#         verbose_name_plural = 'Albuns'

#     def __str__(self):
#         return str(self.id)

class PhotoAlbum(models.Model):
    is_active = models.BooleanField(verbose_name='Ativa/Selecionada?', db_column='is_active', default=False)
    is_profile = models.BooleanField(verbose_name='Perfil?', db_column='is_profile', default=False)
    artist = models.ForeignKey('users.UserArtist', verbose_name='Artista', db_column='artist', blank=False, null=True, on_delete=models.CASCADE, related_name='photos')
    disabled = models.BooleanField(verbose_name='Deletada', db_column='disabled', default=False)
    image = models.CharField(verbose_name='Foto', db_column='image', max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'photo_album'
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return str(self.id)

@receiver(pre_save, sender=PhotoAlbum, dispatch_uid="create_photo")
def change_profile_photo(sender, instance, *args, **kwargs):
    if not instance.id:
        if instance.is_profile == True:
            # artist = user_models.UserArtist.objects.get(id=instance.artist)
            get_all_photos = PhotoAlbum.objects.filter(artist=instance.artist)
            if len(get_all_photos) > 0:
                # CRIANDO FOTO JÁ EXISTINDO PERFIL
                for p in get_all_photos:
                    if p.is_profile == True:
                        p.is_profile = False
                        p.save()
                    else:
                        pass
            else:
                pass
        elif instance.is_profile == False:
            get_all_photos = PhotoAlbum.objects.filter(artist=instance.artist)
            if len(get_all_photos) == 0:
                # CRIANDO PRIMEIRA FOTO DO ARTISTA
                instance.is_profile = True
            else:
                pass
        else:
            pass
    else:
        old_photo = PhotoAlbum.objects.get(id=instance.id)
        if old_photo.is_profile == False and instance.is_profile == True:
            # ATUALIZANDO FOTO DE PERFIL JÁ EXISTENTE
            get_all_photos = PhotoAlbum.objects.filter(artist=instance.artist)
            for p in get_all_photos:
                if p.is_profile == True:
                    p.is_profile = False
                    p.save()
                else:
                    pass