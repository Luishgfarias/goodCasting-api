import sys
import django
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'goodcasting_backend.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goodcasting_backend.settings")
django.setup()

from django.db.models import Q
from django.utils import timezone
from users.serializers import UserArtist, UserArtistSerializer

def change_image():
    instances_artists_without_images = UserArtist.objects.filter(updated_at__gte=timezone.now().replace(hour=0, minute=0, second=0))
    artists_without_images = UserArtistSerializer(instances_artists_without_images, many=True).data
    print('Artists without images: ', len(artists_without_images))
    for artist in artists_without_images:
        if len(artist['photos']) > 0:
            approved = ''
            for photo in artist['photos']:
                if photo['is_active'] == True:
                    approved = photo['image']
                    break
            if approved == '':
                print('Artist: ', artist['id'], ' has no approved photos')
            else:
                instance = UserArtist.objects.get(id=artist['id'])
                instance.image = approved
                instance.save()
        else:
            print('Artist: ', artist['id'], ' has no photos')

if __name__ == '__main__':
    change_image()