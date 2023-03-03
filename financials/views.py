import xmltodict, json, requests, random
import datetime
import ast
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

from .models import Plan, CurrencyPlan
from .serializers import PlanSerializer, CurrencyPlanSerializer
from users import models as user_models

class DefaultPagination(pagination.PageNumberPagination):       
    page_size = 10

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all().order_by('-id')
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['title', 'value',]
    filterset_fields = ('active', 'date_initial', 'date_end',)

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
                        if n.model == 'Financeiro' and n.function == 'Visualizar' and n.active == True:
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
                    serializer = PlanSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = PlanSerializer(data=request.data, context={'request': request})
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
                serializer = PlanSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = PlanSerializer(data=request.data, context={'request': request})
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
                    serializer = PlanSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = PlanSerializer(user)
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
                serializer = PlanSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = PlanSerializer(user)
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
                    serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                    serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = PlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                        if n.model == 'Financeiro' and n.function == 'Excluir' and n.active == True:
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

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = CurrencyPlan.objects.all().order_by('-id')
    serializer_class = CurrencyPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['title', 'value',]
    filterset_fields = ('active', 'date_initial', 'date_end',)

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
                        if n.model == 'Financeiro' and n.function == 'Visualizar' and n.active == True:
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
                    serializer = CurrencyPlanSerializer(data=request.data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Inserir' and n.active == True:
                            permission = permission + 1

                            serializer = CurrencyPlanSerializer(data=request.data, context={'request': request})
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
                serializer = CurrencyPlanSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            serializer = CurrencyPlanSerializer(data=request.data, context={'request': request})
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
                    serializer = CurrencyPlanSerializer(user)
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Visualizar' and n.active == True:
                            permission = permission + 1

                            queryset = self.filter_queryset(self.get_queryset())
                            user = get_object_or_404(queryset, pk=pk)
                            serializer = CurrencyPlanSerializer(user)
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
                serializer = CurrencyPlanSerializer(user)
                return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = get_object_or_404(queryset, pk=pk)
            serializer = CurrencyPlanSerializer(user)
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
                    serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(**serializer.validated_data)
                    return Response(serializer.validated_data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(**serializer.validated_data)
                return Response(serializer.validated_data)
        else:
            instance = self.get_object()
            serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                    serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    user_permissions = user.is_type.permission.all()
                    for n in user_permissions:
                        print(n.model, ' - ', n.function)
                        if n.model == 'Financeiro' and n.function == 'Atualizar' and n.active == True:
                            permission = permission + 1

                            instance = self.get_object()
                            serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = CurrencyPlanSerializer(instance, context={'request': request}, data=request.data, partial=True)
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
                        if n.model == 'Financeiro' and n.function == 'Excluir' and n.active == True:
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