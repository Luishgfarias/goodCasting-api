import sys
from middlewares.middlewares import RequestMiddleware
from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.template import Context, Template

def send_client_invite(email, name, description):
    custom_request = RequestMiddleware(get_response=None)
    custom_request = custom_request.thread_local.current_request
    
    url_base = 'https://' + custom_request.META['HTTP_HOST']
    try:
        #ENVIO DE EMAIL
        template = Template('user_client_invite.html')
        context = Context({
            "email": email,
            "name": name,
            "description": "" if description == None or description == "" else description,
        })
        content = render_to_string('user_client_invite.html', {'context': context})
        send_email = EmailMessage('Convite Good Casting', content, settings.FROM_EMAIL, [email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise

def send_client_rejected(client):
    try:
        #ENVIO DE EMAIL
        template = Template('user_client_rejected.html')
        context = Context({
            "client": client
           
        })
        content = render_to_string('user_client_rejected.html', {'context': context})
        send_email = EmailMessage('Cadastro Good Casting Rejeitado', content, settings.FROM_EMAIL, [client.email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise

def send_client_approved(client):
    try:
        #ENVIO DE EMAIL
        template = Template('user_client_approved.html')
        context = Context({
            "client": client,
           
        })
        content = render_to_string('user_client_approved.html', {'context': context})
        send_email = EmailMessage('Cadastro Aprovado Good Casting', content, settings.FROM_EMAIL, [client.email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise