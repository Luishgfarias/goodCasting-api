import random
import string
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import pagination
from middlewares.middlewares import RequestMiddleware

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import UserManager
from django.db.models.base import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from .models import UserClient, UserAdmin, UserArtist
from .serializers import UserClientSerializer, UserAdminSerializer, UserArtistSerializer, UserArtistPhotosValidSerializer
from utils.images import image_middleware
from emails.artists import send_artist_code

class CheckUserEmail(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_name='validation', url_path='validation', permission_classes=[AllowAny])  
    def user_email(self, request):
        request_user_email = None
        
        request_user_email = request.GET.get('email', "")

        try:
            user = User.objects.get(email=request_user_email)
            return Response({"message": 'User already exists', 'status': status.HTTP_406_NOT_ACCEPTABLE}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except ObjectDoesNotExist:
            return Response({'message': 'User not found', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)


class CheckUserLogged(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_name='logged', url_path='logged', permission_classes=[IsAuthenticated])  
    def user_logged(self, request):
       
        request_user_token = request.META.get('HTTP_AUTHORIZATION', "")

        try:
            user = UserAdmin.objects.get(user__auth_token=request_user_token.replace("Token ", ""))
            serializer = UserAdminSerializer(user)
        except ObjectDoesNotExist:
            try:
                user = UserClient.objects.get(user__auth_token=request_user_token.replace("Token ", ""))
                serializer = UserClientSerializer(user)
            except ObjectDoesNotExist:
                try:
                    user = UserArtist.objects.get(user__auth_token=request_user_token.replace('Token ', ""))
                    serializer = UserArtistSerializer(user)
                except ObjectDoesNotExist:
                    return Response({'error': 'error-user', "message": 'User not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
        response = serializer.data

        return Response(response, status=status.HTTP_200_OK)

class UserAdminAuthentication(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(UserAdminAuthentication, self).post(request, *args, **kwargs)
        token = Token.objects.get(key= response.data['token'])
        user = User.objects.get(auth_token = token)

        user_admin = UserAdmin.objects.get(user=user)
        if user_admin.is_active == True:
            serializer = UserAdminSerializer(user_admin)
        else:
            return Response({'message': 'User is inactive', 'status': status.HTTP_403_FORBIDDEN }, status=status.HTTP_403_FORBIDDEN)      

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserClientAuthentication(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(UserClientAuthentication, self).post(request, *args, **kwargs)
        token = Token.objects.get(key= response.data['token'])
        user = User.objects.get(auth_token = token)

        user_client = UserClient.objects.get(user=user)
        serializer = UserClientSerializer(user_client)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserArtistAuthentication(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(UserArtistAuthentication, self).post(request, *args, **kwargs)
        token = Token.objects.get(key= response.data['token'])
        user = User.objects.get(auth_token = token)

        user_artist = UserArtist.objects.get(user=user)
        if user_artist.first_login == False:
            response = {"first_login": True}
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            user_artist.code = str(code.upper())
            send_artist_code(user_artist, str(code.upper()))
            user_artist.save()
            return Response(response, status=status.HTTP_200_OK)
        else:
            serializer = UserArtistPhotosValidSerializer(user_artist)
        return Response(serializer.data, status=status.HTTP_200_OK)