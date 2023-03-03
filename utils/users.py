from jobs import models as job_models
from supports import models as support_models
from utils.notifications import send_onesignal_to, send_onesignal_to_translation

def verify_jobs(client):
    get_client_jobs = job_models.Solicitation.objects.filter(client=client, status='PENDENTE')
    onesignal_list = []
    if len(get_client_jobs) > 0:
        for job in get_client_jobs:
            job.status = 'EM ANDAMENTO'
            job.save()
            get_all_invites = job_models.SolicitationInvite.objects.filter(job=job)
            for invite in get_all_invites:
                print('tem convite')
                title = {
                    'en': 'New casting',
                    'es': 'Nuevo casting',
                    'pt': 'Novo casting'
                }
                description = {
                    'en': 'You have received a new invite to participante in a casting',
                    'es': 'Has recibido una nueva invitación para participar en un Casting',
                    'pt': 'Você recebeu um novo convite para participar de um casting'
                }
                send_onesignal_to_translation([invite.artist.onesignal_id], title, description, 'New Invitation Notification')
                new_notification = support_models.Notification(artist=invite.artist, title='newInvitationTitle', message='newInvitationDescription')
                new_notification.save()
    else:
        pass
    