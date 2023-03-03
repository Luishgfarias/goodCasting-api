from django.db import models

class ClassManagement(models.Model):
    is_active = models.BooleanField(verbose_name='Ativo?', db_column='is_active', default=False)
    title = models.CharField(verbose_name='Título da Aula', db_column='title', max_length=250, blank=False, null=True)
    subtitle = models.CharField(verbose_name='Subtitulo da Aula', db_column='subtitle', max_length=250, blank=False, null=True)
    link = models.CharField(verbose_name='Link da Aula', db_column='link', max_length=500, blank=False, null=True)
    order = models.IntegerField(verbose_name='Posição', db_column='order', blank=True, null=True, default=0)
    description = models.TextField(verbose_name='Descrição', db_column='description', blank=True, null=False)
    created_at = models.DateTimeField(verbose_name='Criado em', db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Atualizado em', db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'class_management'
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

    def __str__(self):
        return str(self.id)