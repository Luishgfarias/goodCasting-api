from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from utils.choices import NOTIFICATION_CHOICES
from emails.contacts import send_contact_email
from users import models as user_models
from utils.notifications import send_onesignal_to, send_onesignal_to_translation

class ContactForm(models.Model):
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=500, blank=True, null=False)
    email = models.EmailField(verbose_name='Email', db_column='email', blank=True, null=False)
    title = models.CharField(verbose_name='Assunto', db_column='title', max_length=250, blank=False, null=False)
    message = models.TextField(verbose_name='Mensagem', db_column='message', blank=False, null=False)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)

    class Meta:
        db_table = 'contact'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

    def __str__(self):
        return str(self.id)

# Create your models here.
class Notification(models.Model):
  function = models.CharField(verbose_name='Função', db_column='function', max_length=50, blank=True, null=True, choices=NOTIFICATION_CHOICES)
  artist = models.ForeignKey('users.UserArtist', verbose_name='Artista', db_column='artist', blank=True, null=True, on_delete=models.SET_NULL)
  client = models.ForeignKey('users.UserClient', verbose_name='Cliente', db_column='client', blank=True, null=True, on_delete=models.SET_NULL)
  title = models.CharField(verbose_name='Título', db_column='title', max_length=50, blank=False, null=True)
  message = models.TextField(verbose_name='Mensagem', db_column='message', blank=True, null=False)
  visible = models.IntegerField(verbose_name='Visíble', db_column='visible', blank=False, null=True, default=1)
  created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
  updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)


  class Meta:
    db_table = 'notification'
    verbose_name = 'Notificação'
    verbose_name_plural = 'Notificações'

  def __str__(self):
    return str(self.id)

@receiver(post_save, sender=ContactForm, dispatch_uid="create_contact_form")
def send_contact(sender, instance, created, **kwargs):
    if not instance.id:
      send_contact_email(instance)
    else:
      send_contact_email(instance)
      # pass

@receiver(post_save, sender=Notification, dispatch_uid="create_notification")
def send_notification(sender, instance, created, **kwargs):
  
    if created:
      print('CHAMEI FUNCAO')
      title = instance.title
      description = instance.message
      function = send_onesignal_to
      translated = False

      #Titulos
      if instance.title == 'approvedRegistrationTitle':
        function = send_onesignal_to_translation
        translated = True
        title = {
          'en': 'Approved registration',
          'es': 'Registro aprobado',
          'pt': 'Registro aprovado'
        }
      elif instance.title == 'newInvitationTitle':
        function = send_onesignal_to_translation
        translated = True
        title = {
          'en': 'New casting',
          'es': 'Nuevo casting',
          'pt': 'Novo casting'
        }
      elif instance.title == 'selectedModelAcceptedInvitationTitle':
        function = send_onesignal_to_translation
        translated = True
        title = {
          'en': 'Selected artist accepted your invitation',
          'es': 'El artista seleccionado aceptó su invitación',
          'pt': 'Artista selecionado aceitou seu convite'
        }
      elif instance.title == 'selectedParticipateJobTitle':
        function = send_onesignal_to_translation
        translated = True
        title = {
          'en': 'You have been selected to participate in a casting call',
          'es': 'Has sido seleccionado para participar en un casting',
          'pt': 'Você foi selecionado para participar de um casting'
        }

      #Descricoes
      if instance.message == 'approvedRegistrationDescription':
        function = send_onesignal_to_translation
        description = {
          'en': 'His Castings were published. Now just wait for the artists to accept the Casting',
          'es': 'Sus Castings fueron publicados. Ahora solo queda esperar a que los artistas acepten el Casting',
          'pt': 'Seus Casting foram publicados. Agora é só esperar os artistas aceitarem o Casting'
        }
      elif instance.message == 'newInvitationDescription':
        function = send_onesignal_to_translation
        description = {
          'en': 'You have received a new invite to participante in a casting',
          'es': 'Has recibido una nueva invitación para participar en un Casting',
          'pt': 'Você recebeu um novo convite para participar de um casting'
        }
      elif translated == True:
        function = send_onesignal_to_translation
        description = {
          'en': instance.message,
          'es': instance.message,
          'pt': instance.message
        }

      print(title)
      print(description)

      if instance.artist:
        function([instance.artist.onesignal_id], title, description, 'send_message_notification')
      elif instance.client:
        function([instance.client.onesignal_id], title, description, 'send_message_notification')
      elif instance.function and instance.function == 'Modelo':
        onesignal_artist = []
        get_all_models = user_models.UserArtist.objects.all()
        for model in get_all_models:
          if model.onesignal_id:
            onesignal_artist.append(model.onesignal_id)
        function(onesignal_artist, title, description, 'send_message_notification')
      elif instance.function and instance.function == 'Produtor':
        onesignal_client = []
        get_all_models = user_models.UserClient.objects.all()
        for model in get_all_models:
          if model.onesignal_id:
            onesignal_client.append(model.onesignal_id)
        function(onesignal_client, title, description, 'send_message_notification')
      else:
        pass
    else:
      pass
