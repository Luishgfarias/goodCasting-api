from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from utils.choices import TRANSPORT_CHOICES, FOOD_CHOICES, IMAGE_CHOICES, CAMPAIGN_CHOICES, SOLICITATION_STATUS, HAIR_CHOICES, EYE_CHOICES, SKIN_CHOICES, JOB_STATUS
from django.core.validators import MaxValueValidator, MinValueValidator
from utils.solicitations import verify_approved


class Category(models.Model):
    name = models.CharField(verbose_name='Título', db_column='name', max_length=250, blank=False, null=False)
    image = models.ImageField(verbose_name='Imagem', db_column='image', blank=True, null=True, upload_to='category/')
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name

class ArtistProfile(models.Model):
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=500, blank=False, null=False)
    age = models.IntegerField(verbose_name='Idade', db_column='age', blank=True, null=False, default=0)
    age_max = models.IntegerField(verbose_name='Idade Máxima', db_column='age_max', blank=True, null=False, default=0)
    hair = models.CharField(verbose_name='Cabelo', db_column='hair', max_length=100, blank=True, null=False, choices=HAIR_CHOICES)
    eye = models.CharField(verbose_name='Olhos', db_column='eye', max_length=100, blank=True, null=False, choices=EYE_CHOICES)
    skin = models.CharField(verbose_name='Pele', db_column='skin', max_length=100, blank=True, null=False, choices=SKIN_CHOICES)
    stature = models.IntegerField(verbose_name='Altura(150-220cm)', db_column='stature', blank=True, null=True, default=150, validators=[MaxValueValidator(400), MinValueValidator(0)])
    stature_max = models.IntegerField(verbose_name='Altura Máxima(150-220cm)', db_column='stature_max', blank=True, null=True, default=150, validators=[MaxValueValidator(400), MinValueValidator(0)])
    waist = models.IntegerField(verbose_name='Cintura(50-110cm)', db_column='waist', blank=True, null=True, default=50, validators=[MaxValueValidator(400), MinValueValidator(0)])
    waist_max = models.IntegerField(verbose_name='Cintura Máxima(50-110cm)', db_column='waist_max', blank=True, null=True, default=50, validators=[MaxValueValidator(400), MinValueValidator(0)])
    hip = models.IntegerField(verbose_name='Quadril(80-135cm)', db_column='hip', blank=True, null=True, default=80, validators=[MaxValueValidator(400), MinValueValidator(0)])
    hip_max = models.IntegerField(verbose_name='Quadril Máximo(80-135cm)', db_column='hip_max', blank=True, null=True, default=80, validators=[MaxValueValidator(400), MinValueValidator(0)])
    bust = models.IntegerField(verbose_name='Busto(18-80)', db_column='bust', blank=True, null=True, default=18, validators=[MaxValueValidator(400), MinValueValidator(0)])
    bust_max = models.IntegerField(verbose_name='Busto Máximo(18-80)', db_column='bust_max', blank=True, null=True, default=18, validators=[MaxValueValidator(400), MinValueValidator(0)])
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'artist_profile'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.name

class Solicitation(models.Model):
    approved = models.ManyToManyField('users.UserArtist', verbose_name='Lista de Aprovados', db_column='approved', blank=True)
    status = models.CharField(verbose_name='Status', db_column='status', max_length=250, blank=True, null=False, choices=SOLICITATION_STATUS)
    client = models.ForeignKey('users.UserClient', verbose_name='client', db_column='client', blank=False, null=True, on_delete=models.SET_NULL)
    profile = models.ForeignKey(ArtistProfile, verbose_name='Profile', db_column='profile', blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(verbose_name='Job', db_column='title', max_length=250, blank=True, null=False)
    category = models.CharField(verbose_name='Categoria', db_column='category', max_length=250, blank=False, null=False)
    description = models.TextField(verbose_name='Descrição', db_column='description', blank=True, null=False)
    time = models.TimeField(verbose_name='Horário', db_column='time', blank=True, null=True)
    address_street = models.CharField(verbose_name='Rua/Av', db_column='address_street', max_length=400, blank=True, null=False)
    address_neighborhood = models.CharField(verbose_name='Bairro', db_column='address_neighborhood', max_length=400, blank=True, null=False)
    address_number = models.CharField(verbose_name='Número', db_column='address_number', max_length=50, blank=True, null=False)
    address_city = models.CharField(verbose_name='Cidade', db_column='address_city', max_length=100, blank=True, null=False)
    address_state = models.CharField(verbose_name='Estado', db_column='address_state', max_length=100, blank=True, null=False)
    address_complement = models.CharField(verbose_name='Complemento', db_column='address_complement', max_length=400, blank=True, null=False)
    full_address = models.CharField(verbose_name='Endereço Completo(Opcional)', db_column='full_address', max_length=400, blank=True, null=False)
    date = models.DateField(verbose_name='Data', db_column='date', blank=True, null=True, default=None)
    value = models.DecimalField(verbose_name='Cache', db_column='value', max_digits=20, decimal_places=2, blank=True, null=True, default=0.00)
    transport = models.CharField(verbose_name='Transporte', db_column='transport', max_length=250, blank=True, null=False, choices=TRANSPORT_CHOICES)
    feeding = models.CharField(verbose_name='Alimentação', db_column='feeding', max_length=250, blank=True, null=False, choices=FOOD_CHOICES)
    campaign_broadcast = models.CharField(verbose_name='Veiculação de Campanha', db_column='campaign_broadcast', max_length=250, blank=True, null=False, choices=CAMPAIGN_CHOICES)
    image_right_time = models.CharField(verbose_name='Tempo de Direito de Imagem', db_column='image_right_time', max_length=250, blank=True, null=False, choices=IMAGE_CHOICES)
    created_at = models.DateField(verbose_name='Cadastro Realizado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Atualizado Em', db_column='updated_at', editable=False, auto_now=True)

    class Meta:
        db_table = 'job'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def __str__(self):
        return str(self.id)

class SolicitationInvite(models.Model):
    client_evaluated = models.BooleanField(verbose_name='Cliente Avaliado?', db_column='client_evaluated', default=False)
    artist_evaluated = models.BooleanField(verbose_name='Artista Avaliado?', db_column='artist_evaluated', default=False)
    job = models.ForeignKey(Solicitation, verbose_name='Solicitação', db_column='job', blank=False, null=True, on_delete=models.SET_NULL)
    artist = models.ForeignKey('users.UserArtist', verbose_name='User Artista', db_column='artist', blank=False, null=True, on_delete=models.SET_NULL)
    artist_status = models.CharField(verbose_name='Resposta do Artista', db_column='artist_status', max_length=250, blank=True, null=False, choices=JOB_STATUS, default='EM ANALISE')
    client_status = models.CharField(verbose_name='Resposta do Cliente', db_column='client_status', max_length=250, blank=True, null=False, choices=JOB_STATUS, default='EM ANALISE')
    notification_send = models.IntegerField(verbose_name='Notificação enviada', db_column='notification_send', blank=False, null=False, default=0)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)

    class Meta:
        db_table = 'Solicitation_invite'
        verbose_name = 'Job - Convite'
        verbose_name_plural = 'Jobs - Convites'

    def __str__(self):
        return str(self.id)

@receiver(pre_save, sender=SolicitationInvite)
def verify_solicitation_approved(sender, instance=None, created=False, **kwargs):
    if not instance.id:
        pass
    else:
        print('verificando status da solicitação')
        verify_approved(instance)

@receiver(pre_delete, sender=Solicitation, dispatch_uid='delete_invites')
def delete_invites(sender, instance, using, **kwargs):
    if not instance.id:
        pass
    else:
        invites = SolicitationInvite.objects.filter(job=instance.id)

        for invite in invites:
            invite.delete()