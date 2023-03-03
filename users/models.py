from django.db import models
from emails.artists import send_email_artist_approved
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime
import random
import string
from django_random_queryset import RandomManager

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from utils.choices import HAIR_CHOICES, EYE_CHOICES, RECURRING_PAYMENT_CHOICE, SKIN_CHOICES, ARTIST_STATUS, CLIENT_STATUS, GENDER_CHOICES
from django.core.validators import MaxValueValidator, MinValueValidator
from utils.evaluations import add_eval_client, add_eval_artist, remove_eval_client, remove_eval_artist
from jobs import models as job_models

# REMOVE UNIQUE USER CONTRIB EMAIL
User._meta.get_field('email')._unique = False

class UserAdmin(models.Model):
    user = models.OneToOneField(User, verbose_name='Usuário ADM', db_column='user', on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Conta Ativa?', db_column='is_active', default=True)
    is_type = models.ForeignKey('permissions.UserType', verbose_name='Tipo de usuário', db_column='is_type', blank=False, null=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=500, blank=False, null=False)
    email = models.EmailField(verbose_name='Email', db_column='email', blank=False, null=False, unique=True)
    phone = models.CharField(verbose_name='Telefone/Cel', db_column='phone', max_length=100, blank=True, null=False)
    image = models.ImageField(verbose_name='Perfil', db_column='image', blank=True, null=True, upload_to='user/admin/')
    onesignal_id = models.CharField(verbose_name='Id OneSignal', db_column='onesignal_id', max_length=250, blank=True, null=True)
    birth_date = models.DateTimeField(verbose_name="Aniversário",blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'user_admin'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def __str__(self):
        return self.name

class UserClient(models.Model):
    status = models.CharField(verbose_name='Status', db_column='status', max_length=200, blank=True, null=False, choices=CLIENT_STATUS, default='EM ANALISE')
    is_active = models.BooleanField(verbose_name='Conta Ativa?', db_column='is_active', default=True)
    user = models.OneToOneField(User, verbose_name='Usuário ADM', db_column='user', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(verbose_name='Nome Completo', db_column='name', max_length=500, blank=False, null=False)
    trading_name = models.CharField(verbose_name='Nome Fantasia', db_column='trading_name', max_length=500, blank=True, null=False) 
    phone_prefix = models.CharField(verbose_name='Prefixo', db_column='phone_prefix', max_length=10, blank=True, null=False)
    phone = models.CharField(verbose_name='Telefone/Cel', db_column='phone', max_length=50, blank=True, null=False)
    taxpayer = models.CharField(verbose_name='CPF/CNPJ', db_column='taxpayer', max_length=100, blank=True, null=False)
    email = models.EmailField(verbose_name='Email', db_column='email', blank=False, null=False)
    site = models.CharField(verbose_name='Site', db_column='site', max_length=500, blank=True, null=False)
    address_street = models.CharField(verbose_name='Rua/Av', db_column='address_street', max_length=400, blank=True, null=False)
    address_neighborhood = models.CharField(verbose_name='Bairro', db_column='address_neighborhood', max_length=400, blank=True, null=False)
    address_number = models.CharField(verbose_name='Número', db_column='address_number', max_length=50, blank=True, null=False)
    address_city = models.CharField(verbose_name='Cidade', db_column='address_city', max_length=100, blank=True, null=False)
    address_state = models.CharField(verbose_name='Estado', db_column='address_state', max_length=100, blank=True, null=False)
    address_complement = models.CharField(verbose_name='Complemento', db_column='address_complement', max_length=400, blank=True, null=False)
    full_address = models.CharField(verbose_name='Endereço Completo(Opcional)', db_column='full_address', max_length=400, blank=True, null=False)
    image = models.CharField(verbose_name='Foto', db_column='image', max_length=300, blank=True, null=True)
    eval_grade = models.DecimalField(verbose_name='Nota/Média', db_column='eval_grade', max_digits=3, decimal_places=1, blank=True, null=True, default=5.0)
    eval_total = models.IntegerField(verbose_name='Total de Avaliações', db_column='eval_total', blank=True, null=True, default=0)
    onesignal_id = models.CharField(verbose_name='Id OneSignal', db_column='onesignal_id', max_length=250, blank=True, null=True)
    birth_date = models.DateTimeField(verbose_name="Aniversário",db_column="birth_date" ,blank=True, null=True)
    created_at = models.DateField(verbose_name='Cadastro Realizado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Atualizado Em', db_column='updated_at', editable=False, auto_now=True)

    class Meta:
        db_table = 'user_client'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name

class RecurringPaymentType(models.Model):
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=30, blank=False, null=False)
    quantity = models.IntegerField(verbose_name='Quantidade', db_column='quantity', blank=False, null=False)
    type = models.CharField(verbose_name='Tipo', db_column='type', max_length=200, blank=True, null=False, choices=RECURRING_PAYMENT_CHOICE, default='MESES')
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'recurring_payment_type'
        verbose_name = 'Tipo de Pagamento Recorrente'
        verbose_name_plural = 'Tipos de Pagamentos Recorrentes'

    def __str__(self):
        return str(self.name)

class UserArtist(models.Model):
    objects = RandomManager()
    first_login = models.BooleanField(verbose_name='Primeiro login?', db_column='first_login', default=False)
    code = models.CharField(verbose_name='Código', db_column='code', max_length=500, blank=True, null=False)
    user = models.OneToOneField(User, verbose_name='Usuário ADM', db_column='user', on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(verbose_name='Status', db_column='status', max_length=200, blank=True, null=False, choices=ARTIST_STATUS, default='EM ANALISE')
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=500, blank=False, null=False)
    nick_name = models.CharField(verbose_name='Apelido', db_column='nick_name', max_length=250, blank=True, null=False)
    age = models.IntegerField(verbose_name='Idade', db_column='age', blank=True, null=True, default=18)
    gender = models.CharField(verbose_name='Genero', db_column='gender', max_length=50, blank=True, null=False, choices=GENDER_CHOICES)
    birthdate = models.DateField(verbose_name='Data de Nascimento', db_column='birthdate', blank=True, null=True, default=None)
    phone_prefix = models.CharField(verbose_name='Prefixo', db_column='phone_prefix', max_length=10, blank=True, null=False)
    phone = models.CharField(verbose_name='Telefone/Cel', db_column='phone', max_length=50, blank=True, null=False)
    taxpayer = models.CharField(verbose_name='CPF/CNPJ', db_column='taxpayer', max_length=100, blank=True, null=False)
    email = models.EmailField(verbose_name='Email', db_column='email', blank=False, null=False)
    address_street = models.CharField(verbose_name='Rua/Av', db_column='address_street', max_length=400, blank=True, null=False)
    address_neighborhood = models.CharField(verbose_name='Bairro', db_column='address_neighborhood', max_length=400, blank=True, null=False)
    address_number = models.CharField(verbose_name='Número', db_column='address_number', max_length=50, blank=True, null=False)
    address_city = models.CharField(verbose_name='Cidade', db_column='address_city', max_length=100, blank=True, null=False)
    address_state = models.CharField(verbose_name='Estado', db_column='address_state', max_length=100, blank=True, null=False)
    address_complement = models.CharField(verbose_name='Complemento', db_column='address_complement', max_length=400, blank=True, null=False)
    full_address = models.CharField(verbose_name='Endereço Completo(Opcional)', db_column='full_address', max_length=400, blank=True, null=False)
    instagram = models.CharField(verbose_name='Instagram', db_column='instagram', max_length=250, blank=True, null=False)
    approved_at = models.DateTimeField(verbose_name='Aprovado em', db_column='approved_at', blank=True, null=True, default=None)
    hair = models.CharField(verbose_name='Cabelo', db_column='hair', max_length=100, blank=True, null=False, choices=HAIR_CHOICES)
    eye = models.CharField(verbose_name='Olhos', db_column='eye', max_length=100, blank=True, null=False, choices=EYE_CHOICES)
    skin = models.CharField(verbose_name='Pele', db_column='skin', max_length=100, blank=True, null=False, choices=SKIN_CHOICES)
    stature = models.IntegerField(verbose_name='Altura(150-220cm)', db_column='stature', blank=True, null=True, default=150, validators=[MaxValueValidator(400), MinValueValidator(0)])
    waist = models.IntegerField(verbose_name='Cintura(50-110cm)', db_column='waist', blank=True, null=True, default=50, validators=[MaxValueValidator(400), MinValueValidator(0)])
    hip = models.IntegerField(verbose_name='Quadril(80-135cm)', db_column='hip', blank=True, null=True, default=80, validators=[MaxValueValidator(400), MinValueValidator(0)])
    bust = models.IntegerField(verbose_name='Busto(18-80)', db_column='bust', blank=True, null=True, default=18, validators=[MaxValueValidator(400), MinValueValidator(0)])
    eval_grade = models.DecimalField(verbose_name='Nota/Média', db_column='eval_grade', max_digits=3, decimal_places=1, blank=True, null=True, default=5.0)
    eval_total = models.IntegerField(verbose_name='Total de Avaliações', db_column='eval_total', blank=True, null=True, default=0)
    image = models.CharField(verbose_name='Foto', db_column='image', max_length=300, blank=True, null=True)
    onesignal_id = models.CharField(verbose_name='Id OneSignal', db_column='onesignal_id', max_length=250, blank=True, null=True)
    birth_date = models.DateTimeField(verbose_name="Aniversário",blank=True, null=True)
    expiration_date = models.DateTimeField(verbose_name="Data de expiração", db_column='expiration_date', blank=True, null=True)
    recurring_payment_type = models.ForeignKey(RecurringPaymentType, verbose_name='Tipos de Pagamentos Recorrentes', db_column='recurring_payment_type', blank=True, null=True, on_delete=models.DO_NOTHING)
    monthly_fee = models.DecimalField(verbose_name='Valor do Pagamento', db_column='monthly_fee', max_digits=10, decimal_places=2, blank=True, null=True, default=0.0)
    created_at = models.DateField(verbose_name='Cadastro Realizado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Atualizado Em', db_column='updated_at', editable=False, auto_now=True)

    class Meta:
        db_table = 'user_artist'
        verbose_name = 'Artista'
        verbose_name_plural = 'Artistas'

    def __str__(self):
        return str(self.id)

class Tag(models.Model):
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=50, blank=False, null=False)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'tag'
        verbose_name = 'Tag - Avaliação'
        verbose_name_plural = 'Tags - Avaliações'

    def __str__(self):
        return self.name

class EvaluationClient(models.Model):
    hide = models.BooleanField(verbose_name='Ocultar?', db_column='hide', default=False)
    invite = models.ForeignKey('jobs.SolicitationInvite', verbose_name='Job Convite', db_column='invite', blank=True, null=True, on_delete=models.SET_NULL)
    evaluator = models.ForeignKey('users.UserArtist',verbose_name='Avaliador', db_column='evaluator', blank=False, null=True, on_delete=models.CASCADE)
    rated = models.ForeignKey('users.UserClient', verbose_name='Avaliado', db_column='rated',  blank=False, null=False, on_delete=models.CASCADE)
    grade = models.DecimalField(verbose_name='Nota', db_column='grade', max_digits=3, decimal_places=1, blank=False, null=True, default=5.0)
    description = models.TextField(verbose_name='Observação', db_column='description', blank=True, null=False)
    tag = models.ManyToManyField(Tag, verbose_name='Tags', db_column='tag', blank=True)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)

    class Meta:
        db_table = 'evaluation_client'
        verbose_name = 'Cliente - Avaliação'
        verbose_name_plural = 'Clientes - Avaliações'

    def __str__(self):
        return str(self.id)

class EvaluationArtist(models.Model):
    hide = models.BooleanField(verbose_name='Ocultar?', db_column='hide', default=False)
    invite = models.ForeignKey('jobs.SolicitationInvite', verbose_name='Job Convite', db_column='invite', blank=True, null=True, on_delete=models.SET_NULL)
    evaluator = models.ForeignKey('users.UserClient',verbose_name='Avaliador', db_column='evaluator', blank=False, null=True, on_delete=models.CASCADE)
    rated = models.ForeignKey('users.UserArtist', verbose_name='Avaliado', db_column='rated',  blank=False, null=False, on_delete=models.CASCADE)
    grade = models.DecimalField(verbose_name='Nota', db_column='grade', max_digits=3, decimal_places=1, blank=False, null=True, default=5.0)
    description = models.TextField(verbose_name='Observação', db_column='description', blank=True, null=False)
    tag = models.ManyToManyField(Tag, verbose_name='Tags', db_column='tag', blank=True)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)

    class Meta:
        db_table = 'evaluation_artist'
        verbose_name = 'Artista - Avaliação'
        verbose_name_plural = 'Artistas - Avaliações'

    def __str__(self):
        return str(self.id)

# SIGNAL POST SAVE
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    for user in User.objects.all():
        Token.objects.get_or_create(user=user)

@receiver(post_save, sender=EvaluationClient, dispatch_uid="create_evaluation_client")
def create_eval_client(sender, instance, created, **kwargs):
    if created:
        if instance.invite:
            instance.invite.client_evaluated = True
            instance.invite.save()
        else:
            pass
    add_eval_client(instance)

@receiver(post_save, sender=EvaluationArtist, dispatch_uid="create_evaluation_artist")
def create_eval_artist(sender, instance, created, **kwargs):
    if created:
        if instance.invite:
            instance.invite.artist_evaluated = True
            instance.invite.save()
            job = instance.invite.job
            get_all_invites = job_models.SolicitationInvite.objects.filter(job=job, artist_evaluated=False, artist_status='CONFIRMADO', client_status='CONFIRMADO')
            if len(get_all_invites) == 0:
                job.status = 'FINALIZADO'
                job.save()
            else:
                pass
        else:
            pass
    add_eval_artist(instance)

# SIGNAL PRE SAVE
@receiver(pre_save, sender=UserArtist)
def check_artist_status(sender, instance=None, created=False, **kwargs):
    #this function check if user has edited with status REJEITADO and change it to PENDENT again
    if not instance.id:
        pass
    else:
        old_instance = UserArtist.objects.get(id=instance.id)
        if(old_instance.status == "REJEITADO"):
            instance.status = "EM ANALISE"
            
        #check if change email and user not already check login
        if(instance.email != old_instance.email and old_instance.first_login == False and old_instance.status == "APROVADO"):
            password = User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
            instance.user.set_password(password)
            instance.user.save()
            try:
                send_email_artist_approved(instance, password, None)
            except:
                pass 
          
# SIGNAL POST DELETE
@receiver(post_delete, sender=EvaluationClient)
def remove_eval_grade_client(sender, instance=None, **kwargs):
    remove_eval_client(instance)
   
@receiver(post_delete, sender=EvaluationArtist)
def remove_eval_grade_artist(sender, instance=None,  **kwargs):
    remove_eval_artist(instance)
