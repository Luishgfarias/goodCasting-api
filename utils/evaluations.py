from jobs import models as job_models
from users import models as user_models
from django.db.models import Sum, Count
from decimal import Decimal
import math

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

def add_eval_client(instance):
    grade = 0
    eval_count = user_models.EvaluationClient.objects.filter(rated=instance.rated, hide=False).count()
    eval_all_grades = user_models.EvaluationClient.objects.filter(rated=instance.rated, hide=False).values('rated').aggregate(Sum('grade'))
    eval_grade = eval_all_grades['grade__sum']
    
    if eval_count > 0:
        grade = eval_grade / Decimal(eval_count)
    else:
        pass
    
    client = user_models.UserClient.objects.get(id=instance.rated.id)
    client.eval_total = eval_count
    client.eval_grade = normal_round(grade)
    client.save()

def add_eval_artist(instance):
    grade = 0
    eval_count = user_models.EvaluationArtist.objects.filter(rated=instance.rated, hide=False).count()
    eval_all_grades = user_models.EvaluationArtist.objects.filter(rated=instance.rated, hide=False).values('rated').aggregate(Sum('grade'))
    eval_grade = eval_all_grades['grade__sum']
    
    if eval_count > 0:
        grade = eval_grade / Decimal(eval_count)
    else:
        pass
    
    client = user_models.UserArtist.objects.get(id=instance.rated.id)
    client.eval_total = eval_count
    client.eval_grade = normal_round(grade)
    client.save()

def remove_eval_client(instance):
    grade = 0
    eval_count = user_models.EvaluationClient.objects.filter(rated=instance.rated, hide=False).count()
    eval_all_grades = user_models.EvaluationClient.objects.filter(rated=instance.rated, hide=False).values('rated').aggregate(Sum('grade'))
    eval_grade = eval_all_grades['grade__sum']
    
    if eval_count > 0:
        grade = eval_grade / Decimal(eval_count)
    else:
        pass
    
    client = user_models.UserClient.objects.get(id=instance.rated.id)
    client.eval_total = eval_count
    client.eval_grade = normal_round(grade)
    client.save()

def remove_eval_artist(instance):
    grade = 0
    eval_count = user_models.EvaluationArtist.objects.filter(rated=instance.rated, hide=False).count()
    eval_all_grades = user_models.EvaluationArtist.objects.filter(rated=instance.rated, hide=False).values('rated').aggregate(Sum('grade'))
    eval_grade = eval_all_grades['grade__sum']
    
    if eval_count > 0:
        grade = eval_grade / Decimal(eval_count)
    else:
        pass
    
    client = user_models.UserArtist.objects.get(id=instance.rated.id)
    client.eval_total = eval_count
    client.eval_grade = normal_round(grade)
    client.save()
