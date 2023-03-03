from unicodedata import category
import xmltodict, json, requests, random
import datetime
import ast
import pytz
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Q

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

from .models import Category, ArtistProfile, Solicitation, SolicitationInvite
from .serializers import CategorySerializer, ArtistProfileSerializer, SolicitationSerializer, SolicitationInviteSerializer, SolicitationInviteWithApprovedSerializer
from utils.auth_permissions import IsPostOrGetOrIsAuthenticated, IsPostOrIsAuthenticated, IsGetOrIsAuthenticated
from utils.notifications import send_onesignal_to
from supports.models import Notification
from users import models as user_models
from users import serializers as user_serializer
from emails.jobs import send_job_canceled

class DefaultPagination(pagination.PageNumberPagination):       
    page_size = 5
    page_size_query_param = 'page_size'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
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

class SolicitationViewSet(viewsets.ModelViewSet):
    queryset = Solicitation.objects.all().order_by('-id')
    serializer_class = SolicitationSerializer
    permission_classes = [IsPostOrIsAuthenticated,] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'category',]
    filterset_fields = ('status', 'client', 'profile',)


    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
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
                        if n.model == 'Job' and n.function == 'Visualizar' and n.active == True:
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
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = SolicitationSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = SolicitationSerializer(data=request.data, context={'request': request})
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
                serializer = SolicitationSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = SolicitationSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = SolicitationSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = SolicitationSerializer(user)
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
                serializer = SolicitationSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = SolicitationSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = SolicitationSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    self.perform_destroy(instance)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Excluir' and n.active == True:
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
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'], url_name='briefing', url_path='briefing', permission_classes=[AllowAny])  
    def get_briefing_list(self, request):
        request_job = None; request_age = None; request_age_max = None
        request_gender = None; request_hair = None; request_eye = None
        request_skin = None; request_stature = None; request_stature_max = None
        request_waist = None; request_waist_max = None; request_hip = None
        request_hip_max = None; request_bust = None; request_bust_max = None

        request_profile = request.data.get('profile', "")
        request_gender = request.data.get('gender', "")
        request_age = request.data.get('age', "")
        request_age_max = request.data.get('age_max', "")
        request_hair = request.data.get('hair', "")
        request_eye = request.data.get('eye', "")
        request_skin = request.data.get('skin', "")
        request_stature = request.data.get('stature', "")
        request_stature_max = request.data.get('stature_max', "")
        request_waist = request.data.get('waist', "")
        request_waist_max = request.data.get('waist_max', "")
        request_hip = request.data.get('hip', "")
        request_hip_max = request.data.get('hip_max', "")
        request_bust = request.data.get('bust', "")
        request_bust_max = request.data.get('bust_max', "")

        if request_gender != "":
            list_genders = ast.literal_eval(str(request_gender))
            if len(list_genders) <= 0:
                return Response({'error': 'Gender not found'}, status=status.HTTP_400_BAD_REQUEST)

        if request_job != "":
            job = None
            briefing = None
            briefing_list = []
            random_briefing = None
            new_list = []
            job_filters = Q()

            genders = []
            for n in request_gender:
                genders.append(n['name'])
            
            try:
                job_filters &= Q(status='APROVADO') | Q(status='PAUSADO')
                if request_age != "" and request_age_max != "":
                    timezone = pytz.timezone('America/Sao_Paulo')
                    current_date = datetime.datetime.now()
                    current_month = current_date.month
                    current_year = current_date.year
                    max_date = datetime.datetime(year=current_year - request_age_max - 1, month=current_month, day=1)
                    min_date = datetime.datetime(year=current_year - request_age, month=current_month, day=1)
                    max_date = timezone.localize(max_date)
                    min_date = timezone.localize(min_date)
                    job_filters &= Q(birth_date__gte=max_date, birth_date__lte=min_date)
                
                if request_stature != "" and request_stature_max != "":
                    job_filters &= Q(stature__gte=request_stature, stature__lte=request_stature_max)
                
                if request_waist != "" and request_waist_max != "":
                    job_filters &= Q(waist__gte=request_waist, waist__lte=request_waist_max)
                
                if request_hip != "" and request_hip_max != "":
                    job_filters &= Q(hip__gte=request_hip, hip__lte=request_hip_max)
                
                if request_bust != "" and request_bust_max != "":
                    job_filters &= Q(bust__gte=request_bust, bust__lte=request_bust_max)
                
                if request_hair != 'Todos':
                    job_filters &= Q(hair=request_hair)
                if request_eye != 'Todos':
                    job_filters &= Q(eye=request_eye)
                if request_skin != 'Todos':
                    job_filters &= Q(skin=request_skin)
                    

                    
                briefing = list(user_models.UserArtist.objects.filter(job_filters, gender__in=genders))
                queryset = user_models.UserArtist.objects.filter(job_filters, gender__in=genders)
                
                if len(briefing) > 0:
                    briefing_list.extend(briefing)
                    new_list = list(dict.fromkeys(briefing_list))
                else:
                    pass
                
                job_filters = Q()

            except Exception as e:
                return Response({'error': 'error-filter-artist', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = user_serializer.UserArtistWithoutTokenSerializer(new_list, many=True)
            if 'page' in request.query_params:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = user_serializer.UserArtistWithoutTokenSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['job']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['patch'], url_name='approve', url_path='approve', permission_classes=[IsAuthenticated])
    def job_approve(self, request):
        request_job = None
        request_job = request.data.get('job', '')

        if(request_job != ""):
            job = None
            all_invites = None
            try:
                job = Solicitation.objects.get(id=request_job)
            except ObjectDoesNotExist:
                return Response({'error': 'job-not-found', "message": 'Job not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                job.status = "EM ANDAMENTO"


                job.save()
                return Response({'message': 'The Job was approved', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': 'error-job-status', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['job']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['patch'], url_name='canceled', url_path='canceled', permission_classes=[IsAuthenticated])  
    def job_canceled(self, request):
        request_job = None
        request_description = None

        request_job = request.data.get('job', "")
        request_description = request.data.get('description', "")


        if request_job != "" and request_description != "":
            job = None
            try:
                job = Solicitation.objects.get(id=request_job)
            except ObjectDoesNotExist:
                return Response({'error': 'job-not-found', "message": 'Job not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
                
            artists = job.approved.all()
           
            if len(artists) > 0:
                for artist in artists:
                    try:
                        send_job_canceled(artist, request_description, job)
                    except Exception as e:
                        return Response({'error': 'error-send-email', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                pass

            try:
                job.status = 'CANCELADO'
                job.save()
            except Exception as e:
                return Response({'error': 'error-job-status', 'message': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'message': 'The Job was canceled', 'status': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['job']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class SolicitationInviteViewSet(viewsets.ModelViewSet):
    queryset = SolicitationInvite.objects.all().order_by('-id')
    serializer_class = SolicitationInviteSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['artist__name', 'artist__email',]
    filterset_fields = {
        'job': ['exact'], 'job__client': ['exact'], 'artist':['exact'], 
        'artist_status':['in', 'exact'], 'client_status':['in', 'exact'], 
        'job__status':['exact'], 'artist_evaluated':['exact'], 
        'client_evaluated':['exact']
    }


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = SolicitationInviteWithApprovedSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Job' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = SolicitationInviteWithApprovedSerializer(user)
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
                serializer = SolicitationInviteWithApprovedSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = SolicitationInviteWithApprovedSerializer(user)
            return Response(serializer.data)

    @action(detail=False, methods=['get'], url_name='group-chats', url_path='group-chats', permission_classes=[AllowAny])
    def get_invite_solicitation_chats(self, request):
        request_invite_list = request.GET.get('invites', '')
        request_user_type = request.GET.get('user_type', 'Artista')
        if(request_invite_list != ''):
            invite_list = json.loads(request_invite_list)
            group_chats = []
            
            try:
                invite = SolicitationInvite.objects.filter(id__in=invite_list, job__status="EM ANDAMENTO").order_by("-job__id")
                for n in invite:
                    if request_user_type == "Cliente":
                        if n.job != None and n.artist != None: #check if job has not none
                            if(len(group_chats) > 0):
                                try:
                                    index = next((index for (index, d) in enumerate(group_chats) if d["job"] == n.job.id))
                                    # if n.artist != None:
                                    group_chats[index]["invites"].append({
                                        "id": n.id,
                                        "user_image": n.artist.image,
                                        "user_name": n.artist.name,
                                        "user_id": n.artist.id
                                    })
                                except:
                                    # if n.artist != None:
                                    group_chats.append({
                                        "job": n.job.id,
                                        "category": n.job.category,
                                        "description": n.job.description,
                                        "client_id": n.job.client.id if n.job.client else 0,
                                        "client_name": n.job.client.name if n.job.client else "",
                                        "invites": [{
                                            "id": n.id,
                                            "user_image": n.artist.image,
                                            "user_name": n.artist.name,
                                            "user_id": n.artist.id
                                        }]
                                    })
                            else:
                                # if n.artist != None:
                                group_chats.append({
                                    "job": n.job.id,
                                    "category": n.job.category,
                                    "description": n.job.description,
                                    "client_id": n.job.client.id if n.job.client else 0,
                                    "client_name": n.job.client.name if n.job.client else "",
                                    "invites": [{
                                        "id": n.id,
                                        "user_image": n.artist.image,
                                        "user_name": n.artist.name,
                                        "user_id": n.artist.id
                                    }]
                                })
                    else:
                        if n.job != None and n.artist != None: #check if job has not none
                            if(len(group_chats) > 0):
                                try:
                                    index = next((index for (index, d) in enumerate(group_chats) if d["job"] == n.job.id))
                                    group_chats[index]["invites"].append({
                                        "id": n.id,
                                        "user_image": '',
                                        "user_name": n.job.client.name if n.job.client else '',
                                        "user_id": n.job.client.id if n.job.client else 0
                                    })
                                except:
                                    group_chats.append({
                                        "job": n.job.id,
                                        "category": n.job.category,
                                        "description": n.job.description,
                                        "client_id": n.job.client.id if n.job.client else 0,
                                        "client_name": n.job.client.name if n.job.client else "",
                                        "invites": [{
                                            "id": n.id,
                                            "user_image": '',
                                            "user_name": n.job.client.name if n.job.client else '',
                                            "user_id": n.job.client.id if n.job.client else 0
                                        }]
                                    })
                            else:

                                group_chats.append({
                                    "job": n.job.id,
                                    "category": n.job.category,
                                    "description": n.job.description,
                                    "client_id": n.job.client.id if n.job.client else 0,
                                    "client_name": n.job.client.name if n.job.client else "",
                                    "invites": [{
                                        "id": n.id,
                                        "user_image": '',
                                        "user_name": n.job.client.name if n.job.client else '',
                                        "user_id": n.job.client.id if n.job.client else 0
                                    }]
                                })

            except ObjectDoesNotExist:
                return Response({"group_chats": []})

            

            return Response({"group_chats": group_chats})
        else:
            return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['invites']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_name='send', url_path='send', permission_classes=[AllowAny])  
    def send_solicitation_invites(self, request):
        request_artists = None
        request_client = None
        request_job = None
        list_artists = []

        request_artists = request.data.get('artists', "")
        request_client = request.data.get('client', "")
        request_job = request.data.get('job', "")

        if request_artists != "":
            list_artists = ast.literal_eval(str(request_artists))
            if len(list_artists) <= 0:
                return Response({'error': 'Artists not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            list_artists = request_artists

        if request_client != '' and request_job != '':
            client = None
            job = None
            invites = []
            inviter = None
            artist = None

            try:
                client = user_models.UserClient.objects.get(id=request_client)
            except ObjectDoesNotExist:
                return Response({'error': 'user-not-found', "message": 'User not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                job = Solicitation.objects.get(id=request_job)
            except ObjectDoesNotExist:
                return Response({'error': 'solicitation-not-found', "message": 'Solicitation not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            for artist in list_artists:
                # print(artist)
                if 'id' in artist:
                    artist = user_models.UserArtist.objects.get(id=artist['id'])
                    invite = SolicitationInvite(artist=artist, job=job)
                    invite.save()
                    invites.append(invite)
                else:
                    return Response({'error': 'artist-error', "message": 'Fields job and artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)


            serializer = SelectedSolicitationSerializer(selected, many=True) 
            response = serializer.data

            return Response(response, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['client', 'job']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ArtistProfileViewSet(viewsets.ModelViewSet):
    queryset = ArtistProfile.objects.all().order_by('-id')
    serializer_class = ArtistProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name',]

    def list(self, request, *args, **kwargs):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
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
                        if n.model == 'Profile' and n.function == 'Visualizar' and n.active == True:
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
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))

                if user.is_type.is_superuser:
                    serializer = ArtistProfileSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Profile' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = ArtistProfileSerializer(data=request.data, context={'request': request})
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
                serializer = ArtistProfileSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = ArtistProfileSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


    def retrieve(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
                
                if user.is_type.is_superuser:
                    print('é super usuário')
                    queryset = self.filter_queryset(self.get_queryset())
                    user = get_object_or_404(queryset, pk=pk)
                    serializer = ArtistProfileSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Profile' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = ArtistProfileSerializer(user)
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
                serializer = ArtistProfileSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = ArtistProfileSerializer(user)
            return Response(serializer.data)
        
    def update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Profile' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response(serializer.validated_data)
    
    def partial_update(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é super usuário')
                    instance = self.get_object()
                    serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Profile' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = ArtistProfileSerializer(instance, context={'request': request}, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, pk=None):
        header_user = request.META.get('HTTP_AUTHORIZATION', None)
        if header_user != None:
            user = None
            permission = 0
            try:
                user = user_models.UserAdmin.objects.get(user__auth_token=header_user.replace("Token ", ""))
            
                if user.is_type.is_superuser:
                    print('é superusuario')
                    instance = self.get_object()
                    self.perform_destroy(instance)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Profile' and n.function == 'Excluir' and n.active == True:
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