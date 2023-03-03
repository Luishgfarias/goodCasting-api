import sys
import django
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'goodcasting_backend.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goodcasting_backend.settings")
django.setup()

from jobs.models import SolicitationInvite, Solicitation
from supports.models import Notification

def send_notification():
    current_casting = Solicitation.objects.filter(
        status="EM ANDAMENTO", 
        created_at__gt="2022-06-29" #data inicial do CRON para evitar que convites passadores recebram o casting novamente
    )
    for cast in current_casting: 
        current_invites = SolicitationInvite.objects.filter(job=cast.id)

        for invite in current_invites:
            if(invite.notification_send == 0 and invite.artist is not None):
                if(invite.artist.onesignal_id):
                    try:
                        new_notification = Notification(artist=invite.artist, title='newInvitationTitle', message='newInvitationDescription')
                        new_notification.save()

                        invite.notification_send = 1
                        invite.save()
                    except Exception as e:
                        print(str(e))

if __name__ == '__main__':
    send_notification()