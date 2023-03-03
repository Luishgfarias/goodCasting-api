import requests, base64, json
from django.http import JsonResponse
from django.conf import settings

def send_onesignal_to(player_ids, title, msg, about):
    json_data = {
        "app_id": settings.APP_ID,
        "include_player_ids": player_ids,
        "contents": {"en": msg },
        "headings": {"en": title },
        "data": {"type": 'new-solicitation'}
    }

    resp = requests.post(
        'https://onesignal.com/api/v1/notifications', 
        data=json.dumps(json_data).encode('utf-8'),
        headers={'content-type':'application/json',"Authorization": "Basic " + settings.APP_KEY} 
    )  
    # if resp.status_code != requests.codes.ok: # diferente de http 200
    #     print(
    #         'OneSignal Error request:',
    #         'Tipo de notificação:', about,
    #         'Code:', resp.status_code,
    #         'Message:', resp.text,
    #         'OneSignal Ids:', player_ids,
    #     )
    # else:
    #     print(
    #         'OneSignal Success request:',
    #         'Tipo de notificação:', about,
    #         'Code:', resp.status_code,
    #         'Message:', resp.text,
    #         'OneSignal Ids:', player_ids,
    #     )

def send_onesignal_to_translation(player_ids, title, msg, about):
    json_data = {
        "app_id": settings.APP_ID,
        "include_player_ids": player_ids,
        "contents": msg,
        "headings": title,
        "data": {"type": 'new-solicitation'}
    }

    resp = requests.post(
        'https://onesignal.com/api/v1/notifications', 
        data=json.dumps(json_data).encode('utf-8'),
        headers={'content-type':'application/json',"Authorization": "Basic " + settings.APP_KEY} 
    )  
    # if resp.status_code != requests.codes.ok: # diferente de http 200
    #     print(
    #         'OneSignal Error request:',
    #         'Tipo de notificação:', about,
    #         'Code:', resp.status_code,
    #         'Message:', resp.text,
    #         'OneSignal Ids:', player_ids,
    #     )
    # else:
    #     print(
    #         'OneSignal Success request:',
    #         'Tipo de notificação:', about,
    #         'Code:', resp.status_code,
    #         'Message:', resp.text,
    #         'OneSignal Ids:', player_ids,
    #     )

def send_onesignal(segmento, titulo, mensagem):
    json_data = {
        "app_id": settings.APP_ID,
        "included_segments": [segmento.onesignal],
        "contents": {"en": mensagem },
        "headings": {"en": titulo }
    }

    resp = requests.post(
        'https://onesignal.com/api/v1/notifications', 
        data=json.dumps(json_data).encode('utf-8'),
        headers={'content-type':'application/json',"Authorization": "Basic " + settings.APP_KEY} 
    )   

    # if resp.status_code != requests.codes.ok: # diferente de http 200
    #     print(resp.text) # erro
    # else:
    #     print(resp.text)