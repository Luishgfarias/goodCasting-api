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
from jobs.models import SolicitationInvite

def delete_null_invites():
    instances = SolicitationInvite.objects.filter(job=None)
    for instance in instances:
        instance.delete()

if __name__ == '__main__':
    delete_null_invites()