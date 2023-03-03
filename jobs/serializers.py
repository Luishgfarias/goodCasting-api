from middlewares.middlewares import RequestMiddleware
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist
from django.core.files.base import ContentFile
from .models import Category, ArtistProfile, Solicitation, SolicitationInvite
from jobs import models as job_models
from users import models as user_models
from users import serializers as user_serializers
from supports import models as support_models
# from utils import messages
from utils.notifications import send_onesignal_to

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['image'] = '' if instance.image == "" or instance.image == None else url_image + instance.image.url
        return response

class ArtistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistProfile
        fields = ['id', 'name', 'age', 'age_max', 'hair', 'eye', 'skin', 'stature', 'stature_max', 'waist', 'waist_max',
                  'hip', 'hip_max', 'bust', 'bust_max', 'created_at', 'updated_at']

class SolicitationSerializer(serializers.ModelSerializer):
    artist_count = serializers.SerializerMethodField('get_artist_count', read_only=True)
    # approved = user_serializers.UserArtistWithoutTokenSerializer(many=True, read_only=True)
    class Meta:
        model = Solicitation
        fields = ['id','status', 'title', 'category', 'description', 'time', 'address_street',
                  'address_neighborhood', 'address_number', 'address_city', 'address_state', 'address_complement', 'full_address',
                  'date', 'value', 'transport', 'feeding', 'campaign_broadcast', 'image_right_time', 'created_at', 'updated_at', 'client', 'profile', 'artist_count' ]
    
    def get_artist_count(self, request):
        artists = request.approved
        count = artists.all().count()
        return count


    def create(self, request):
        context = self.context['request'].data
        client = user_models.UserClient.objects.get(id=context['client'])
        new_solicitation = None
        new_solicitation = super(SolicitationSerializer, self).create(request)     
        new_solicitation.status = "PENDENTE"

        new_solicitation.save()
        if 'invites' in context and 'invite_all' not in context:
            print('convites')
            invites = []
            onesignal_list = []
            notifications = []
            new_notification = None
            try:
                for artist in context['invites']:
                    if 'id' in artist:
                        artist = user_models.UserArtist.objects.get(id=artist['id'])
                        invite = job_models.SolicitationInvite(artist=artist, job=new_solicitation)
                        invite.save()
                        # if client.status == 'APROVADO':
                        #     print('enviando notificação, aprvado')
                        #     new_notification = support_models.Notification(artist=artist, title='newInvitationTitle', message='newInvitationDescription')
                        #     new_notification.save()
                        #     invites.append(invite)
                        #     notifications.append(new_notification)
                        #     # send_onesignal_to([artist.onesignal_id], 'newInvitationTitle', 'newInvitationDescription', 'New Invitation Notification')
                        # else:
                        #     print('nao aprovado')
                        #     pass
                    else:
                        raise serializers.ValidationError(str(e))
            except Exception as e:
                if new_solicitation is not None:
                    new_solicitation.delete()
                if new_notification is not None:
                    new_notification.delete()
                if len(invites) > 0:
                    for invete in invites:
                        invete.delete()
                if len(notifications) > 0:
                    for n in notifications:
                        n.delete()
                raise serializers.ValidationError(str(e))
        
        if 'invite_all' in context and 'invites' not in context: 
            print('convite all')
            invites = []
            onesignal_list = []
            notifications = []
            new_notification = None
            try:
                get_all_artists = user_models.UserArtist.objects.filter(status='APROVADO')
                if len(get_all_artists) > 0:
                    for artist in get_all_artists:
                        invite = job_models.SolicitationInvite(artist=artist, job=new_solicitation)
                        invite.save()
                        # if client.status == 'APROVADO':
                        #     print('enviando notificação, aprvado')
                        #     new_notification = support_models.Notification(artist=artist, title='newInvitationTitle', message='newInvitationDescription')
                        #     new_notification.save()
                        #     invites.append(invite)
                        #     notifications.append(new_notification)
                        #     # send_onesignal_to([artist.onesignal_id], 'newInvitationTitle', 'newInvitationDescription', 'New Invitation Notification')
                        # else:
                        #     print('nao aprovado')
                        #     pass
            except Exception as e:
                if new_solicitation is not None:
                    new_solicitation.delete()
                if new_notification is not None:
                    new_notification.delete()
                if len(invites) > 0:
                    for invete in invites:
                        invete.delete()
                if len(notifications) > 0:
                    for n in notifications:
                        n.delete()
                raise serializers.ValidationError(str(e))

        return new_solicitation
    
    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['profile'] = '' if instance.profile == "" or instance.profile == None else ArtistProfileSerializer(instance.profile).data
        response['client'] = '' if instance.client == "" or instance.client == None else user_serializers.UserClientWithoutTokenSerializer(instance.client).data
        return response

class SolicitationWithApprovedSerializer(serializers.ModelSerializer):
    artist_count = serializers.SerializerMethodField('get_artist_count', read_only=True)
    approved = user_serializers.UserArtistApprovedSerializer(many=True, read_only=True)
    class Meta:
        model = Solicitation
        fields = ['id','status', 'title', 'category', 'description', 'time', 'address_street', 'approved',
                  'address_neighborhood', 'address_number', 'address_city', 'address_state', 'address_complement', 'full_address',
                  'date', 'value', 'transport', 'feeding', 'campaign_broadcast', 'image_right_time', 'created_at', 'updated_at', 'client', 'profile', 'artist_count' ]
    
    def get_artist_count(self, request):
        artists = request.approved
        count = artists.all().count()
        return count


    def create(self, request):
        context = self.context['request'].data
        client = user_models.UserClient.objects.get(id=context['client'])
        new_solicitation = None
        new_solicitation = super(SolicitationSerializer, self).create(request)     
        new_solicitation.status = "PENDENTE"

        new_solicitation.save()
        if 'invites' in context and 'invite_all' not in context:
            print('convites')
            invites = []
            onesignal_list = []
            notifications = []
            new_notification = None
            try:
                for artist in context['invites']:
                    if 'id' in artist:
                        artist = user_models.UserArtist.objects.get(id=artist['id'])
                        invite = job_models.SolicitationInvite(artist=artist, job=new_solicitation)
                        invite.save()
                        # if client.status == 'APROVADO':
                        #     print('enviando notificação, aprvado')
                        #     new_notification = support_models.Notification(artist=artist, title='newInvitationTitle', message='newInvitationDescription')
                        #     new_notification.save()
                        #     invites.append(invite)
                        #     notifications.append(new_notification)
                        #     # send_onesignal_to([artist.onesignal_id], 'newInvitationTitle', 'newInvitationDescription', 'New Invitation Notification')
                        # else:
                        #     print('nao aprovado')
                        #     pass
                    else:
                        raise serializers.ValidationError(str(e))
            except Exception as e:
                if new_solicitation is not None:
                    new_solicitation.delete()
                if new_notification is not None:
                    new_notification.delete()
                if len(invites) > 0:
                    for invete in invites:
                        invete.delete()
                if len(notifications) > 0:
                    for n in notifications:
                        n.delete()
                raise serializers.ValidationError(str(e))
        
        if 'invite_all' in context and 'invites' not in context: 
            print('convite all')
            invites = []
            onesignal_list = []
            notifications = []
            new_notification = None
            try:
                get_all_artists = user_models.UserArtist.objects.filter(status='APROVADO')
                if len(get_all_artists) > 0:
                    for artist in get_all_artists:
                        invite = job_models.SolicitationInvite(artist=artist, job=new_solicitation)
                        invite.save()
                        # if client.status == 'APROVADO':
                        #     print('enviando notificação, aprvado')
                        #     new_notification = support_models.Notification(artist=artist, title='newInvitationTitle', message='newInvitationDescription')
                        #     new_notification.save()
                        #     invites.append(invite)
                        #     notifications.append(new_notification)
                        #     # send_onesignal_to([artist.onesignal_id], 'newInvitationTitle', 'newInvitationDescription', 'New Invitation Notification')
                        # else:
                        #     print('nao aprovado')
                        #     pass
            except Exception as e:
                if new_solicitation is not None:
                    new_solicitation.delete()
                if new_notification is not None:
                    new_notification.delete()
                if len(invites) > 0:
                    for invete in invites:
                        invete.delete()
                if len(notifications) > 0:
                    for n in notifications:
                        n.delete()
                raise serializers.ValidationError(str(e))

        return new_solicitation
    
    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['profile'] = '' if instance.profile == "" or instance.profile == None else ArtistProfileSerializer(instance.profile).data
        response['client'] = '' if instance.client == "" or instance.client == None else user_serializers.UserClientWithoutTokenSerializer(instance.client).data
        return response

class SolicitationInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitationInvite
        fields = ['id', 'client_evaluated', 'artist_evaluated', 'job', 'artist', 'artist_status', 'client_status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['job'] = '' if instance.job == "" or instance.job == None else SolicitationSerializer(instance.job).data
        response['artist'] = '' if instance.artist == "" or instance.artist == None else user_serializers.UserArtistWithoutTokenSerializer(instance.artist).data
        return response

class SolicitationInviteWithApprovedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitationInvite
        fields = ['id', 'client_evaluated', 'artist_evaluated', 'job', 'artist', 'artist_status', 'client_status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['job'] = '' if instance.job == "" or instance.job == None else SolicitationWithApprovedSerializer(instance.job).data
        response['artist'] = '' if instance.artist == "" or instance.artist == None else user_serializers.UserArtistWithoutTokenSerializer(instance.artist).data
        return response
    
    
class SolicitationInviteWithoutTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitationInvite
        fields = ['id', 'client_evaluated', 'artist_evaluated', 'job', 'artist', 'artist_status', 'client_status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['job'] = '' if instance.job == "" or instance.job == None else SolicitationSerializer(instance.job).data
        response['artist'] = '' if instance.artist == "" or instance.artist == None else user_serializers.UserArtistWithoutTokenSerializer(instance.artist).data
        return response
    