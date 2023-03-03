from django.db import models
from decimal import Decimal

from users.models import UserArtist
from utils.choices import PLAN_CHOICES

# Create your models here.
class Plan(models.Model):
  title = models.CharField(verbose_name='Título', db_column='title', max_length=50, blank=True, null=False)
  value = models.DecimalField(verbose_name="Valor", db_column="value", max_digits=20, decimal_places=2, blank=False, null=True, default=0.00)
  date_initial = models.DateField(verbose_name="Data Inicial", db_column="date_initial", blank=False, null=True, default=None)
  active = models.BooleanField(verbose_name="Ativo", db_column="active", default=False)
  date_end = models.DateField(verbose_name="Data Final", db_column="date_end", blank=False, null=True, default=None)
  created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True, null=True)
  updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True, null=True)

  class Meta:
    db_table = 'plan'
    verbose_name = 'Plano'
    verbose_name_plural = 'Planos'

  def __str__(self):
    return str(self.id)

class CurrencyPlan(models.Model):
  artist = models.ForeignKey(UserArtist, on_delete=models.SET_NULL, null=True)
  plan = models.OneToOneField(Plan, on_delete=models.SET_NULL, null=True)
  status = models.CharField(verbose_name='Status', db_column='status', max_length=50, blank=False, null=True, choices=PLAN_CHOICES)

  class Meta:
    db_table = 'currency_plan'
    verbose_name = 'Mensalidade'
    verbose_name_plural = 'Mensalidades'

  def __str__(self):
    return str(self.id)