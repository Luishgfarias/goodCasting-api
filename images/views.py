import xmltodict, json, requests
import datetime
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

from .models import PhotoAlbum
from .serializers import PhotoAlbumSerializer

class DefaultPagination(pagination.PageNumberPagination):       
    page_size = 10

class PhotoAlbumViewSet(viewsets.ModelViewSet):
    queryset = PhotoAlbum.objects.all().order_by('-id')
    serializer_class = PhotoAlbumSerializer
    permission_classes = [IsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('artist', 'is_active', 'disabled')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)