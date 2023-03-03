import sys

from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.template import Context, Template

def send_job_canceled(user, description, job):
    try:
        #ENVIO DE EMAIL
        template = Template('job_canceled.html')
        context = Context({
            "user": user,
            "job": job,
            "description": description
           
        })
        content = render_to_string('job_canceled.html', {'context': context})
        send_email = EmailMessage('Job Cancelado', content, settings.FROM_EMAIL, [user.email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise