import xmltodict, json, requests
import datetime
import ast
import re
from django.shortcuts import get_list_or_404, get_object_or_404
from  more_itertools import unique_everseen

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework.filters import SearchFilter

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import UserManager
from django.db.models.base import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from .models import RecurringPaymentType, Tag, UserAdmin, UserClient, UserArtist, EvaluationClient, EvaluationArtist
from images import models as image_models
from utils.auth_permissions import IsPostOrGetOrIsAuthenticated, IsPostOrIsAuthenticated, IsGetOrIsAuthenticated
from .serializers import RecurringPaymentTypeSerializer, TagSerializer, UserAdminSerializer, UserArtistPhotosValidSerializer, UserArtistSerializer, UserArtistLandingPageSerializer, UserClientSerializer, EvaluationClientSerializer, EvaluationArtistSerializer, UserArtistOnlyPhotosValidSerializer
from emails.clients import send_client_invite, send_client_approved, send_client_rejected
from emails.artists import send_email_artist_approved, send_artist_rejected
from supports import models as support_models
from utils.users import verify_jobs
from utils.notifications import send_onesignal_to, send_onesignal_to_translation



class ClassClientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    class Meta:
        model = UserClient
        fields = ['status', 'email', 'taxpayer', 'phone_prefix', 'address_city', 'address_state', 'full_address']

class ClassArtistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    nick_name = django_filters.CharFilter(field_name='nick_name', lookup_expr='icontains')
    # phone = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')
    class Meta:
        model = UserArtist
        fields = ['status', 'gender', 'age', 'email', 'taxpayer', 'bust', 'waist', 'hip', 'stature', 'hair', 'eye', 'skin', 'phone_prefix', 'address_city', 'address_state', 'full_address']

class DefaultPagination(pagination.PageNumberPagination):       
    page_size = 10

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name',]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class EvaluationClientViewSet(viewsets.ModelViewSet):
    queryset = EvaluationClient.objects.all().order_by('-id')
    serializer_class = EvaluationClientSerializer
    permission_classes = [IsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['grade',]
    filterset_fields = ('hide', 'rated', 'evaluator', 'invite',)

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                print('é Usuário Admin')
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())

                    if 'page' in request.query_params:
                        page = self.paginate_queryset(queryset)
                        if page is not None:
                            serializer = self.get_serializer(page, many=True)
                            return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Cliente' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1
                        
                            queryset = self.filter_queryset(self.get_queryset())
                        
                            if 'page' in request.query_params:
                                page = self.paginate_queryset(queryset)
                                if page is not None:
                                    serializer = self.get_serializer(page, many=True)
                                    return self.get_paginated_response(serializer.data)

                            serializer = self.get_serializer(queryset, many=True)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
                
            except ObjectDoesNotExist:
                print('Não é admin')
                queryset = self.filter_queryset(self.get_queryset())
                if 'page' in request.query_params:
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            print('sem token')
            queryset = self.filter_queryset(self.get_queryset())
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = EvaluationClientSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Cliente' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = EvaluationClientSerializer(data=request.data, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                serializer = EvaluationClientSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = EvaluationClientSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = EvaluationClientSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Cliente' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = EvaluationClientSerializer(user)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                queryset = self.filter_queryset(self.get_queryset())
                user = get_object_or_404(queryset, pk=pk)
                serializer = EvaluationClientSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = EvaluationClientSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Cliente' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(**serializer.validated_data)
                            return Response(serializer.validated_data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação cliente' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = EvaluationClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    self.perform_destroy(instance)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Cliente' and n.function == 'Excluir' and n.active == True:
                            permission = permission + 1
                            instance = self.get_object()
                            self.perform_destroy(instance)
                    
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                instance = self.get_object()
                self.perform_destroy(instance)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)

class EvaluationArtistViewSet(viewsets.ModelViewSet):
    queryset = EvaluationArtist.objects.all().order_by('-id')
    serializer_class = EvaluationArtistSerializer
    permission_classes = [IsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['grade',]
    filterset_fields = ('hide', 'rated', 'evaluator', 'invite',)

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                print('é Usuário Admin')
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())

                    if 'page' in request.query_params:
                        page = self.paginate_queryset(queryset)
                        if page is not None:
                            serializer = self.get_serializer(page, many=True)
                            return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1
                        
                            queryset = self.filter_queryset(self.get_queryset())
                        
                            if 'page' in request.query_params:
                                page = self.paginate_queryset(queryset)
                                if page is not None:
                                    serializer = self.get_serializer(page, many=True)
                                    return self.get_paginated_response(serializer.data)

                            serializer = self.get_serializer(queryset, many=True)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
                
            except ObjectDoesNotExist:
                print('Não é admin')
                queryset = self.filter_queryset(self.get_queryset())
                if 'page' in request.query_params:
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            print('sem token')
            queryset = self.filter_queryset(self.get_queryset())
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = EvaluationArtistSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = EvaluationArtistSerializer(data=request.data, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                serializer = EvaluationArtistSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = EvaluationArtistSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = EvaluationArtistSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = EvaluationArtistSerializer(user)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                queryset = self.filter_queryset(self.get_queryset())
                user = get_object_or_404(queryset, pk=pk)
                serializer = EvaluationArtistSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = EvaluationArtistSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(**serializer.validated_data)
                            return Response(serializer.validated_data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = EvaluationArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    self.perform_destroy(instance)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Avaliação Artista' and n.function == 'Excluir' and n.active == True:
                            permission = permission + 1
                            instance = self.get_object()
                            self.perform_destroy(instance)
                    
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                instance = self.get_object()
                self.perform_destroy(instance)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
    
    @action(detail=False, methods=['get'], url_name='tags', url_path='tags', permission_classes=[AllowAny])  
    def get_artist_tags(self, request):
        request_artist = None

        request_artist = request.GET.get('artist', "")

        if request_artist != "":
            artist = None
            list_eval = []
            final_list = []
            try:
                artist = UserArtist.objects.get(id=request_artist)
            except ObjectDoesNotExist:
                return Response({'error': 'artist-not-found', "message": 'Artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            get_all_evaluations = EvaluationArtist.objects.filter(rated=artist)
            if len(get_all_evaluations) > 0:
                for evaluation in get_all_evaluations:
                    for tag in evaluation.tag.all():
                        if tag in list_eval:
                            pass
                        else:
                            obj = {
                                'id': tag.id,
                                'name': tag.name
                            }
                            list_eval.append(obj)
                final_list = list(unique_everseen(list_eval))       
            else:
                pass

            return Response(final_list, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['artist']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = UserAdmin.objects.all().order_by('id')
    serializer_class = UserAdminSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'phone', 'email', 'taxpayer',]
    filterset_fields = ('is_active', 'email', 'is_type')

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        print(header_user)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                print(user)
                print('é Usuário Admin')
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())

                    if 'page' in request.query_params:
                        page = self.paginate_queryset(queryset)
                        if page is not None:
                            serializer = self.get_serializer(page, many=True)
                            return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1
                        
                            queryset = self.filter_queryset(self.get_queryset())
                        
                            if 'page' in request.query_params:
                                page = self.paginate_queryset(queryset)
                                if page is not None:
                                    serializer = self.get_serializer(page, many=True)
                                    return self.get_paginated_response(serializer.data)

                            serializer = self.get_serializer(queryset, many=True)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
                
            except ObjectDoesNotExist:
                print('Não é admin')
                queryset = self.filter_queryset(self.get_queryset())
                if 'page' in request.query_params:
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            print('sem token')
            queryset = self.filter_queryset(self.get_queryset())
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = UserAdminSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = UserAdminSerializer(data=request.data, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                serializer = UserAdminSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = UserAdminSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = UserAdminSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = UserAdminSerializer(user)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                queryset = self.filter_queryset(self.get_queryset())
                user = get_object_or_404(queryset, pk=pk)
                serializer = UserAdminSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserAdminSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(**serializer.validated_data)
                            return Response(serializer.validated_data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = UserAdminSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    self.perform_destroy(instance)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Admin' and n.function == 'Excluir' and n.active == True:
                            permission = permission + 1
                            instance = self.get_object()
                            self.perform_destroy(instance)
                    
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                instance = self.get_object()
                self.perform_destroy(instance)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)

class UserArtistViewSet(viewsets.ModelViewSet):
    queryset = UserArtist.objects.filter(user__is_active=True).order_by('-id')
    serializer_class = UserArtistSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'phone', 'email', 'taxpayer',]
    filter_class = ClassArtistFilter
    # filterset_fields = (
    #     'status', 'gender', 'age', 'email', 'taxpayer', 'bust', 'waist', 'hip', 'stature', 'hair', 'eye', 'skin', 'phone', 'phone_prefix', 'address_city', 'address_state', 'full_address')

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        phone_params = request.query_params.get("phone", "")
        if header_user != None:
            user = None
            permission = 0
            try:
                print('1')
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                print('é Usuário Admin')
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = []
                    if phone_params != "":
                        for n in self.filter_queryset(self.get_queryset()):
                            if n.phone != "":
                                artist_phone = re.sub('[^A-Za-z0-9]+', '', n.phone)
                                if phone_params in artist_phone:
                                    queryset.append(n)
                        
                    else:
                        queryset = self.filter_queryset(self.get_queryset())

                    if 'page' in request.query_params:
                        page = self.paginate_queryset(queryset)
                        if page is not None:
                            serializer = self.get_serializer(page, many=True)
                            return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1
                            queryset = []
                            if phone_params != "":
                                for n in self.filter_queryset(self.get_queryset()):
                                    if n.phone != "":
                                        artist_phone = re.sub('[^A-Za-z0-9]+', '', n.phone)
                                        if phone_params in artist_phone:
                                            queryset.append(n)
                            else:
                                queryset = self.filter_queryset(self.get_queryset())
                        
                            if 'page' in request.query_params:
                                page = self.paginate_queryset(queryset)
                                if page is not None:
                                    serializer = self.get_serializer(page, many=True)
                                    return self.get_paginated_response(serializer.data)

                            serializer = self.get_serializer(queryset, many=True)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
                
            except ObjectDoesNotExist:
                print('Não é admin')
                queryset = self.filter_queryset(self.get_queryset())
                if 'page' in request.query_params:
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            print('sem token')
            queryset = self.filter_queryset(self.get_queryset())
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = UserArtistSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = UserArtistSerializer(data=request.data, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                serializer = UserArtistSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = UserArtistSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = UserArtistOnlyPhotosValidSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = UserArtistOnlyPhotosValidSerializer(user)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                queryset = self.filter_queryset(self.get_queryset())
                user = get_object_or_404(queryset, pk=pk)
                serializer = UserArtistOnlyPhotosValidSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserArtistOnlyPhotosValidSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserArtistSerializer(instance, context={'request': request} ,data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(**serializer.validated_data)
                            return Response(serializer.validated_data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = UserArtistSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserArtistPhotosValidSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserArtistPhotosValidSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserArtistPhotosValidSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = UserArtistPhotosValidSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                import uuid
                email_id = uuid.uuid4().hex

                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    instance.user.username =   str(email_id) + "@inactive.com"
                    instance.user.email =   str(email_id) + "@inactive.com"
                    instance.user.is_active = False
                    instance.user.save()
                    instance.status = "REJEITADO"
                    instance.save()
                    Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Artista' and n.function == 'Excluir' and n.active == True:
                            permission = permission + 1
                            instance = self.get_object()
                            instance.user.username =   str(email_id) + "@inactive.com"
                            instance.user.email =   str(email_id) + "@inactive.com"
                            instance.user.is_active = False
                            instance.user.save()
                            instance.status = "REJEITADO"
                            instance.save()
                            Response(status=status.HTTP_204_NO_CONTENT)
                    
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                # self.perform_destroy(instance)
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_name='briefing-artist', url_path='briefing-artist', permission_classes=[AllowAny])
    def briefing_artist(self, request):
        artist_id = request.query_params.get('artist', '')

        if(artist_id != ""):
            try:
                artist = UserArtist.objects.get(id=artist_id)
                serializer = UserArtistOnlyPhotosValidSerializer(artist)
                return Response(serializer.data)
            except ObjectDoesNotExist:
                return Response({'error': 'artist-not-found', "message": 'Artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['artist']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_name='code', url_path='code', permission_classes=[AllowAny])  
    def verify_artist_code(self, request):
        request_code = None

        request_code = request.data.get('code', "")

        if request_code != "":
            user = None
            try:
                user = UserArtist.objects.get(code=request_code)
            except ObjectDoesNotExist:
                return Response({'error': 'user-not-found', 'message': 'User not found', 'status':status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            user.first_login = True
            user.save()

            serializer = UserArtistSerializer(user)
            response = serializer.data

            return Response(response, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['code']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_name='rejected', url_path='rejected', permission_classes=[IsAuthenticated])  
    def send_artist_rejected(self, request):
        request_reason = None
        request_description = None
        request_artist = None

        request_artist = request.data.get('artist', "")
       

        if request_artist != "":
            artist = None
            status_artist = 'EM ANALISE'
            try:
                artist = UserArtist.objects.get(id=request_artist)
            except ObjectDoesNotExist:
                return Response({'error': 'artist-not-found', "message": 'Artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            try:
                status_artist = 'REJEITADO'
                artist.status = status_artist
                artist.save()
                send_artist_rejected(artist)
            except Exception as e:
                if status_artist == 'REJEITADO':
                    artist.status = 'EM ANALISE'
                    artist.save()
                return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'User was rejected', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['artist']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_name='approved', url_path='approved', permission_classes=[IsAuthenticated])  
    def send_artist_approved(self, request):
        request_artist = None

        request_artist = request.data.get('artist', "")

        if request_artist != "":
            artist = None
            status_artist = 'EM ANALISE'
            images = None
            try:
                artist = UserArtist.objects.get(id=request_artist)
            except ObjectDoesNotExist:
                return Response({'error': 'artist-not-found', "message": 'Artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            get_artist_images = image_models.PhotoAlbum.objects.filter(artist=artist, is_active=True)
            if len(get_artist_images) > 0:
                images = get_artist_images

            try:
                status_artist = 'APROVADO'
                artist.status = status_artist
                current_date = datetime.datetime.now()
                amount_day_expire = 0
                
                try:
                    if(artist.recurring_payment_type is not None):
                        recurring = RecurringPaymentType.objects.get(id=artist.recurring_payment_type.id)

                        if(recurring.type == "DIAS"):
                            amount_day_expire = recurring.quantity
                        elif(recurring.type == "MESES"):
                            amount_day_expire = recurring.quantity * 30
                        else:
                            amount_day_expire = recurring.quantity * 365
                        
                        artist.expiration_date = current_date + datetime.timedelta(days=amount_day_expire)

                    else:
                        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'O artista precisa ter uma tipo de recorrência',
                        'fields': ['recurring_payment_type']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except Exception as e:
                    return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'O artista precisa ter uma tipo de recorrência',
                        'fields': ['recurring_payment_type']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                artist.approved_at = current_date
                password = User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
                artist.user.set_password(password)
                artist.user.save()
                artist.save()
                send_email_artist_approved(artist, password, images)
                # send_onesignal_to([client.onesignal_id], onesignal_message, onesignal_title, 'Registration approval notification')
            except Exception as e:
                if status_artist == 'APROVADO':
                    artist.status = 'EM ANALISE'
                    artist.save()
                return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'User was been approved', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['artist']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_name='status', url_path='status', permission_classes=[AllowAny])  
    def check_status(self, request):
        artist_id = None

        artist_id = request.query_params.get('artist', '')

        if artist_id != "":
            artist = None
            try:
                artist = UserArtist.objects.get(id=artist_id)
            except ObjectDoesNotExist:
                return Response({'error': 'user-not-found', 'message': 'User not found', 'status':status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            
            if artist.status == 'REJEITADO':
                return Response({'error': 'not-allow', 'status': status.HTTP_403_FORBIDDEN, 
                        'response': {'message':'user rejected'}}, 
                        status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'ok': 'ok'}, status=status.HTTP_200_OK)

        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['code']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    @action(detail=False, methods=['get'], url_name='get-four-talents', url_path='get-four-talents', permission_classes=[AllowAny])  
    def get_talents_for_landing_page(self, request):
        artists_id_list = request.GET.get('artists_id_list', "")
        print(artists_id_list)
        ids_array = []
        if artists_id_list != "":
            ids_array = artists_id_list.split(",")
 
        artists = UserArtist.objects.filter(status="APROVADO").exclude(id__in=ids_array)
        randomized_artists = artists.random(4)
        serializer = UserArtistLandingPageSerializer(randomized_artists, many=True)
        response = serializer.data

        return Response(response, status=status.HTTP_200_OK)

class UserClientViewSet(viewsets.ModelViewSet):
    queryset = UserClient.objects.filter(user__is_active=True).order_by('-id')
    serializer_class = UserClientSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'phone', 'email', 'taxpayer', 'trading_name',]
    filter_class = ClassClientFilter
    # filterset_fields = ('status', 'email', 'taxpayer', 'phone', 'phone_prefix', 'address_city', 'address_state', 'full_address')

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        phone_params = request.query_params.get("phone", "")
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                print('é Usuário Admin')
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = []
                    if phone_params != "":
                        for n in self.filter_queryset(self.get_queryset()):
                            if n.phone != "":
                                artist_phone = re.sub('[^A-Za-z0-9]+', '', n.phone)
                                if phone_params in artist_phone:
                                    queryset.append(n)
                    else:
                        queryset = self.filter_queryset(self.get_queryset())

                    if 'page' in request.query_params:
                        page = self.paginate_queryset(queryset)
                        if page is not None:
                            serializer = self.get_serializer(page, many=True)
                            return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1
                        
                            queryset = []
                            if phone_params != "":
                                for n in self.filter_queryset(self.get_queryset()):
                                    if n.phone != "":
                                        artist_phone = re.sub('[^A-Za-z0-9]+', '', n.phone)
                                        if phone_params in artist_phone:
                                            queryset.append(n)
                            else:
                                queryset = self.filter_queryset(self.get_queryset())
                        
                            if 'page' in request.query_params:
                                page = self.paginate_queryset(queryset)
                                if page is not None:
                                    serializer = self.get_serializer(page, many=True)
                                    return self.get_paginated_response(serializer.data)

                            serializer = self.get_serializer(queryset, many=True)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
                
            except ObjectDoesNotExist:
                print('Não é admin')
                queryset = self.filter_queryset(self.get_queryset())
                if 'page' in request.query_params:
                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            print('sem token')
            queryset = self.filter_queryset(self.get_queryset())
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = UserClientSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = UserClientSerializer(data=request.data, context={'request': request})
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                serializer = UserClientSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = UserClientSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = UserClientSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = UserClientSerializer(user)
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                queryset = self.filter_queryset(self.get_queryset())
                user = get_object_or_404(queryset, pk=pk)
                serializer = UserClientSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserClientSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(**serializer.validated_data)
                            return Response(serializer.validated_data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response(serializer.data)
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                instance = self.get_object()
                serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = UserClientSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    import uuid
                    instance = self.get_object()
                    instance.user.username = uuid.uuid4().hex + "@inactive.com"
                    instance.user.is_active = False
                    instance.user.save()
                    instance.status = "REJEITADO"
                    instance.save()
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Cliente' and n.function == 'Excluir' and n.active == True:
                            permission = permission + 1
                            import uuid
                            instance = self.get_object()
                            instance.user.username = uuid.uuid4().hex + "@inactive.com"
                            instance.user.is_active = False
                            instance.user.save()
                            instance.status = "REJEITADO"
                            instance.save()
                    
                        else:
                            pass
                        
                        if permission >= 1:
                            break
                    if permission == 0:
                        return Response({'error': 'error-user-forbidden',
                                        "message": "The request was ok, but it was refused or access was not allowed.",
                                        'status': status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                print("ENTROU NO 4")
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
    
    @action(detail=False, methods=['post'], url_name='invite', url_path='invite', permission_classes=[IsAuthenticated])  
    def send_client_invite(self, request):
        request_email = None
        request_name = None
        request_description = None

        request_email = request.data.get('email', "")
        request_name = request.data.get('name', "")
        request_description = request.data.get('description', "")

        if request_email != "" and request_name != "":
            try:
                send_client_invite(request_email, request_name, request_description)
            except Exception as e:
                return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'message': 'Your Invitation has been sent successfully', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['email', 'name']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_name='rejected', url_path='rejected', permission_classes=[IsAuthenticated])  
    def send_client_rejected(self, request):
        request_reason = None
        request_description = None
        request_client = None

        request_client = request.data.get('client', "")

        if request_client != "":
            client = None
            status_client = 'EM ANALISE'
            try:
                client = UserClient.objects.get(id=request_client)
            except ObjectDoesNotExist:
                return Response({'error': 'client-not-found', "message": 'Client not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            try:
                status_client = 'REJEITADO'
                client.status = status_client
                client.save()
                send_client_rejected(client)
            except Exception as e:
                if status_client == 'REJEITADO':
                    client.status = 'EM ANALISE'
                    client.save()
                return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'User was rejected', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['client']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_name='approved', url_path='approved', permission_classes=[IsAuthenticated])  
    def send_client_approved(self, request):
        request_client = None
        request_client = request.data.get('client', "")

        if request_client != "":
            client = None
            new_notification = None
            onesignal_list = []
            status_client = 'EM ANALISE'
            try:
                client = UserClient.objects.get(id=request_client)
                if client.onesignal_id:
                    onesignal_list.append(client.onesignal_id)
            except ObjectDoesNotExist:
                return Response({'error': 'client-not-found', "message": 'Client not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            try:
                status_client = 'APROVADO'
                client.status = status_client
                client.save()
                # verify_jobs(client) do not approve job when client is aproved anymore.
                send_client_approved(client)
                new_notification = support_models.Notification(client=client, title='approvedRegistrationTitle', message='approvedRegistrationDescription')
                new_notification.save()
                title = {
                    'en': 'Approved registration',
                    'es': 'Registro aprobado',
                    'pt': 'Registro aprovado'
                }
                description = {
                    'en': 'His Castings were published. Now just wait for the artists to accept the Casting',
                    'es': 'Sus Castings fueron publicados. Ahora solo queda esperar a que los artistas acepten el Casting',
                    'pt': 'Seus Casting foram publicados. Agora é só esperar os artistas aceitarem o Casting'
                }
                send_onesignal_to_translation(onesignal_list, title, description, 'Registration approval notification')
            except Exception as e:
                if status_client == 'APROVADO':
                    client.status = 'EM ANALISE'
                    client.save()
                if new_notification is not None:
                    new_notification.delete()
                return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'User was been approved', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['client']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecurringPaymentTypeViewSet(viewsets.ModelViewSet):
    queryset = RecurringPaymentType.objects.all()
    serializer_class = RecurringPaymentTypeSerializer
    permission_classes = [IsAuthenticated]