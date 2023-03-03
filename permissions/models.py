from django.db import models
from utils.choices import FUNCTION_CHOICES, MODEL_CHOICES

class Permission(models.Model):
    function = models.CharField(verbose_name='Funcionalidade', db_column='function', max_length=200, blank=False, null=False, choices=FUNCTION_CHOICES)
    model = models.CharField(verbose_name='Modelo', db_column='model', max_length=200, blank=False, null=False, choices=MODEL_CHOICES)
    active = models.BooleanField(verbose_name='Ativo', db_column='active', default=True)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'permission'
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'

    def __str__(self):
        return "{} - {}".format(self.model, self.function)

class UserType(models.Model):
    name = models.CharField(verbose_name='Nome', db_column='name', max_length=500, blank=False, null=False)
    permission = models.ManyToManyField(Permission, verbose_name='Permissão', blank=True, related_name='user_types')
    active = models.BooleanField(verbose_name='Ativo', db_column='active', default=True)
    is_superuser = models.BooleanField(verbose_name='Status de superusuário?', db_column='is_superuser', default=False)
    is_staff = models.BooleanField(verbose_name='É Membro da Equipe?', db_column='is_staff', default=False)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'user_type'
        verbose_name = 'Tipo de Usuário'
        verbose_name_plural = 'Tipos de Usuário'

    def __str__(self):
        return self.name
