import xmltodict, json, requests
import datetime
import ast
from django.shortcuts import get_list_or_404, get_object_or_404
from itertools import chain

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

from django.shortcuts import render

from .models import Notification, ContactForm
from .serializers import NotificationSerializer, ContactFormSerializer
from utils.auth_permissions import IsPostOrGetOrIsAuthenticated, IsPostOrIsAuthenticated, IsGetOrIsAuthenticated
from users import models as user_models
from jobs import models as job_models
from utils.notifications import send_onesignal_to

class DefaultPagination(pagination.PageNumberPagination):       
    page_size = 10

class ContactFormViewSet(viewsets.ModelViewSet):
    queryset = ContactForm.objects.all().order_by('-id')
    serializer_class = ContactFormSerializer
    permission_classes = [IsPostOrIsAuthenticated] 
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'email', 'title',]
    filterset_fields = ('email',)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     if 'page' in request.query_params:
    #         page = self.paginate_queryset(queryset)
    #         if page is not None:
    #             serializer = self.get_serializer(page, many=True)
    #             return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

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
                      if n.model == 'Contato' and n.function == 'Visualizar' and n.active == True:
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
                  serializer = ContactFormSerializer(data=request.data, context={'request': request})
                  serializer.is_valid(raise_exception=True)
                  serializer.save()
                  return Response(serializer.data)
              else:
                  user_permissions = user.is_type.permission.all()
                  for n in user_permissions:
                      print(n.model, ' - ', n.function)
                      if n.model == 'Contato' and n.function == 'Inserir' and n.active == True:
                          permission = permission + 1

                          serializer = ContactFormSerializer(data=request.data, context={'request': request})
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
              serializer = ContactFormSerializer(data=request.data, context={'request': request})
              serializer.is_valid(raise_exception=True)
              serializer.save()
              return Response(serializer.data)
        else:
            serializer = ContactFormSerializer(data=request.data, context={'request': request})
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
                  serializer = ContactFormSerializer(user)
                  return Response(serializer.data)
              else:
                  user_permissions = user.is_type.permission.all()
                  for n in user_permissions:
                      print(n.model, ' - ', n.function)
                      if n.model == 'Contato' and n.function == 'Visualizar' and n.active == True:
                          permission = permission + 1

                          queryset = self.filter_queryset(self.get_queryset())
                          user = get_object_or_404(queryset, pk=pk)
                          serializer = ContactFormSerializer(user)
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
              serializer = ContactFormSerializer(user)
              return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = ContactFormSerializer(user)
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
                  serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
                  serializer.is_valid(raise_exception=True)
                  serializer.save(**serializer.validated_data)
                  return Response(serializer.validated_data)
              else:
                  user_permissions = user.is_type.permission.all()
                  for n in user_permissions:
                      print(n.model, ' - ', n.function)
                      if n.model == 'Contato' and n.function == 'Atualizar' and n.active == True:
                          permission = permission + 1

                          instance = self.get_object()
                          serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
              serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
              serializer.is_valid(raise_exception=True)
              serializer.save(**serializer.validated_data)
              return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                  serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
                  serializer.is_valid(raise_exception=True)
                  serializer.save()
                  return Response(serializer.data)
              else:
                  user_permissions = user.is_type.permission.all()
                  for n in user_permissions:
                      print(n.model, ' - ', n.function)
                      if n.model == 'Contato' and n.function == 'Atualizar' and n.active == True:
                          permission = permission + 1

                          instance = self.get_object()
                          serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
              serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
              serializer.is_valid(raise_exception=True)
              serializer.save()
              return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = ContactFormSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                      if n.model == 'Contato' and n.function == 'Excluir' and n.active == True:
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

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-id')
    serializer_class = NotificationSerializer
    permission_classes = [IsPostOrIsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['function__name', 'artist__name', 'artist__email', 'client__name', 'client__email', 'title', ]
    filterset_fields = {
        'artist': ['in', 'exact'],
        'client': ['in', 'exact'],
        'function': ['in', 'exact'],
        'visible': ['exact']
    }

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
                        if n.model == 'Notificação' and n.function == 'Visualizar' and n.active == True:
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
                    serializer = NotificationSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Notificação' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = NotificationSerializer(data=request.data, context={'request': request})
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
                serializer = NotificationSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = NotificationSerializer(data=request.data, context={'request': request})
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
                    serializer = NotificationSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Notificação' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = NotificationSerializer(user)
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
                serializer = NotificationSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = NotificationSerializer(user)
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
                    serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Notificação' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                    serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Notificação' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = NotificationSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                        if n.model == 'Notificação' and n.function == 'Excluir' and n.active == True:
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
    
    @action(detail=False, methods=['get'], url_path='list', url_name='list')
    def list_notifications(self, request):
        request_user = None
        
        request_user = request.GET.get('user', "")
        request_app = request.GET.get('app', "")
        request_page = request.GET.get('page', None)

        if request_user != "" and request_app != "":
            user = None
            client = None
            artist = None
            app_client = None
            app_artist = None
            function = ""
            result_list = []
            
            if request_app == "Client":
                try:
                    user = user_models.UserClient.objects.get(id=request_user)
                    function = 'Produtor'
                except ObjectDoesNotExist:
                    return Response({'error': 'client-not-found', "message": 'Client not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            elif request_app == "Artist":
                try:
                    user = user_models.UserArtist.objects.get(id=request_user)
                    function = 'Modelo'
                except ObjectDoesNotExist:
                    return Response({'error': 'artist-not-found', "message": 'Artist not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({'error': 'app-not-found', "message": 'App not found', 'status': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)


            if function == 'Produtor':
                client = Notification.objects.filter(client=user, visible=1)
                app_client = Notification.objects.filter(function='Produtor', visible=1, client=None)
                result_list = list(chain(client, app_client))
            elif function == 'Modelo':
                artist = Notification.objects.filter(artist=user, visible=1)
                app_artist = Notification.objects.filter(function='Modelo', visible=1, artist=None)
                result_list = list(chain(artist, app_artist))
            else:
                pass
            
            if(request_page is not None):
                page = self.paginate_queryset(result_list)

                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

            serializer = NotificationSerializer(result_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['user', 'app']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            



    
    # send new message post
    @action(detail=False, methods=['post'], url_path='message', url_name='message')
    def newMessageNotification(self, request):
        request_from = None
        request_to_type = None
        request_to = None
        request_solicitation_id = None

        request_from = request.data.get('from', "")
        request_to_type = request.data.get('to_type', "")
        request_to = request.data.get('to', "")
        request_solicitation_id = request.data.get('job', "")
        
        if request_from != '' and request_to_type != '' and request_to != '' and request_solicitation_id != '':
            user_to = ""
            user_from = ""
            if request_to_type == 'client':
                try:
                    user_to = user_models.UserClient.objects.get(id=request_to)
                    try:
                        user_from = user_models.UserArtist.objects.get(id=request_from)
                    except ObjectDoesNotExist:
                        return Response({'mensagem': 'Client not found'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                except ObjectDoesNotExist:
                    return Response({'mensagem': 'Client not found'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            elif request_to_type == 'artist':
                try:
                    user_to = user_models.UserArtist.objects.get(id=request_to)
                    try:
                        user_from = user_models.UserClient.objects.get(id=request_from)
                    except ObjectDoesNotExist:
                        return Response({'mensagem': 'Client not found'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except ObjectDoesNotExist:
                    return Response({'mensagem': 'Client not found'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            try:
                solicitation = job_models.SolicitationInvite.objects.get(id=request_solicitation_id)
            except ObjectDoesNotExist:
                return Response({'mensagem': 'Job not found'}, status=status.HTTP_406_NOT_ACCEPTABLE)
             
            try: 
                onesignal_ids = []
                if request_to_type == 'client':
                    onesignal_ids.append(user_to.onesignal_id)
                elif request_to_type == 'artist':
                    onesignal_ids.append(user_to.onesignal_id)
                
                send_onesignal_to(onesignal_ids, 'GoodCasting', "There's a new message for you from {} about the job {}.".format(user_from.name, solicitation.job.category), 'Send Notification Message')
                return Response({'mensagem': 'Notification sent to {} from {} successfully!'.format(user_to.name, user_from.name)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'status':status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'error-required-fields', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        'response': {'message':'you need to submit all required fields', 
                        'fields': ['from', 'to_type', 'to', 'job']}}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
