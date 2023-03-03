import xmltodict, json, requests
from datetime import date

import ast
from django.shortcuts import get_list_or_404, get_object_or_404

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import UserManager
from django.db.models.base import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from .models import Tag, UserAdmin, UserClient, UserArtist, EvaluationClient, EvaluationArtist
from images import models as image_models
from .serializers import TagSerializer, UserAdminSerializer, UserArtistSerializer, UserClientSerializer, EvaluationClientSerializer, EvaluationArtistSerializer
from utils.users import verify_jobs

class UserClientChartViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_name='client', url_path='client')  
    def client_chart(self, request):
        now = date.today()
        last_month = now.month-1 if now.month > 1 else 12
        last_year = now.year - 1
        get_all_clients = UserClient.objects.all().count()

        if now.month == 1:
            get_last_month_clients = UserClient.objects.filter(created_at__month=last_month, created_at__year=last_year).count()
        else:
            get_last_month_clients = UserClient.objects.filter(created_at__month=last_month, created_at__year=now.year).count()
        
        get_actual_month_clients = UserClient.objects.filter(created_at__month=8).count()
        
        diff = get_actual_month_clients - get_last_month_clients
      
        if diff > 0 and get_last_month_clients > 0:
            percentage = (diff / get_last_month_clients) * 100
        else:
            percentage = 0.0
        
        return Response({'percentage': percentage, 
                         "count": get_all_clients,
                         "month": now.month, 
                         "year": now.year,
                         "month_count": get_actual_month_clients, 
                         "last_month": last_month, 
                         'last_year': last_year,
                         "last_month_count": get_last_month_clients}, 
                         status=status.HTTP_200_OK)


class UserArtistChartViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_name='artist', url_path='artist')  
    def artist_chart(self, request):
        now = date.today()
        last_month = now.month-1 if now.month > 1 else 12
        last_year = now.year - 1
        get_all_artist = UserArtist.objects.all().count()

        if now.month == 1:
            get_last_month_artists = UserArtist.objects.filter(created_at__month=last_month, created_at__year=last_year).count()
        else:
            get_last_month_artists = UserArtist.objects.filter(created_at__month=last_month, created_at__year=now.year).count()
        
        get_actual_month_artists = UserArtist.objects.filter(created_at__month=8).count()
        
        diff = get_actual_month_artists - get_last_month_artists
      
        percentage = (diff / get_last_month_artists) * 100
        
        
        return Response({'percentage': percentage,
                         "count": get_all_artist, 
                         "month": now.month, 
                         "year": now.year,
                         "month_count": get_actual_month_artists, 
                         "last_month": last_month, 
                         'last_year': last_year,
                         "last_month_count": get_last_month_artists}, 
                         status=status.HTTP_200_OK)
