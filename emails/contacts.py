import sys
from middlewares.middlewares import RequestMiddleware

from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.template import Context, Template

def custom_request():
    #request customizado
    request = RequestMiddleware(get_response=None)
    request = request.thread_local.current_request
    new_request = 'http://' + request.META['HTTP_HOST'] 
    return new_request

def send_contact_email(contact):
    # url_base = custom_request()
    try:
        #ENVIO DE EMAIL
        print("Template")
        template = Template('contact_form.html')
        context = Context({
            "contact": contact,
            "base_url": "goodcasting.pt",
           
        })
        print("Context")
        content = render_to_string('contact_form.html', {'context': context})
        print("Ant Send email")
        send_email = EmailMessage('Ajuda Good Casting', content, settings.FROM_EMAIL, settings.TO_RECEIVE)
        print("Pos Send email")
        send_email.content_subtype = 'html'
        # if contact.image:
        #     content_type = mimetypes.guess_type(contact.image.name)[0] # change is here <<<
        #     send_email.attach(contact.image.name, contact.image.read(), content_type)
        print("Send Send email")
        send_email.send()
        print("Pos Send email")
    except:
        print('erro ao enviar email', sys.exc_info()[0])
        raise