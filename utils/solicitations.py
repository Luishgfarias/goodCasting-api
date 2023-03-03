from jobs import models as job_models
from supports import models as support_models
from utils.notifications import send_onesignal_to, send_onesignal_to_translation

def verify_approved(instance):
    old_job = job_models.SolicitationInvite.objects.get(id=instance.id)
    job = instance.job
    new_notification_client = None
    new_notification_artist = None
    artist = instance.artist
    client = instance.job.client
    onesignal_client = []
    onesignal_artist = []

    try:
        if old_job.artist_status == "EM ANALISE" and instance.artist_status == "CONFIRMADO":
            if client.onesignal_id:
                onesignal_client.append(client.onesignal_id)
            title = {
                'en': 'Selected artist accepted your invitation',
                'es': 'El artista seleccionado aceptó su invitación',
                'pt': 'Artista selecionado aceitou seu convite'
            }
            description = {
                'en': str(job.category),
                'es': str(job.category),
                'pt': str(job.category)
            }
            # send_onesignal_to_translation(onesignal_client, title, description, 'send-selected-message-artist')
            new_notification_client = support_models.Notification(client=client, title='selectedModelAcceptedInvitationTitle', message=str(job.category))
            new_notification_client.save()

        if old_job.client_status == "EM ANALISE" and instance.client_status == "CONFIRMADO":
            if artist.onesignal_id:
                onesignal_artist.append(artist.onesignal_id)
            title = {
                'en': 'You have been selected to participate in a casting call',
                'es': 'Has sido seleccionado para participar en un casting',
                'pt': 'Você foi selecionado para participar de um casting'
            }
            description = {
                'en': str(job.category),
                'es': str(job.category),
                'pt': str(job.category)
            }
            # send_onesignal_to_translation(onesignal_artist, title, description, 'send-confirm-message-artist'  )
            new_notification_artist = support_models.Notification(artist=artist, title='selectedParticipateJobTitle', message=str(job.category))
            new_notification_artist.save()

        if old_job.artist_status != instance.artist_status and old_job.client_status != instance.client_status or (old_job.artist_status != instance.artist_status or (old_job.client_status != instance.client_status)):
            if instance.artist_status == 'CONFIRMADO' and instance.client_status == 'CONFIRMADO':
                print('cliente aprovado, inserido na solicitação')
                job.approved.add(artist)
                job.save()
            else:
                print('Status foi alterado, mas ainda não aprovado')
                pass
    except:
        raise Exception('Ocorreu uma falha ao alterar seu endereço. Por favor, tente novamente mais tarde')

    else:
        print('Valores de status não foram modificados')
        pass
