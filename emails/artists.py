import sys
from middlewares.middlewares import RequestMiddleware

from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.template import Context, Template

def send_artist_code(artist, code):
    try:
        #ENVIO DE EMAIL
        template = Template('user_artist_code.html')
        context = Context({
            "code": '' if code == None or code == "" else code,
           
        })
        content = render_to_string('user_artist_code.html', {'context': context})
        send_email = EmailMessage('Código de Verificação Good Casting', content, settings.FROM_EMAIL, [artist.email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise

def send_artist_rejected(artist):
    try:
        #ENVIO DE EMAIL
        template = Template('user_artist_rejected.html')
        context = Context({
            "artist": artist,
           
        })
        content = render_to_string('user_artist_rejected.html', {'context': context})
        send_email = EmailMessage('Cadastro Good Casting Rejeitado', content, settings.FROM_EMAIL, [artist.email])
        send_email.content_subtype = 'html'
        send_email.send()
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise

def send_email_artist_approved(artist, password, images):
    custom_request = RequestMiddleware(get_response=None)
    custom_request = custom_request.thread_local.current_request
    
    url_base = 'https://' + custom_request.META['HTTP_HOST']
    try:
        #ENVIO DE EMAIL
        template = Template('user_artist_approved.html')
        context = Context({
            "artist": artist,
            "password": password,
            "url_base": url_base,
            "images": [] if images == None or images == "" else images,
        })
        content = render_to_string('user_artist_approved.html', {'context': context})
        send_email = EmailMessage('Cadastro Aprovado Good Casting', content, settings.FROM_EMAIL, [artist.email])
        send_email.content_subtype = 'html'
        send_email.send()
        # print("######################")
        # print("ENVIANDO ", artist.email)
        # print("######################")
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise