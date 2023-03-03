from asyncore import read
from dataclasses import field
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist
from django.core.files.base import ContentFile
from .models import RecurringPaymentType, Tag, UserClient, UserAdmin, UserArtist, EvaluationClient, EvaluationArtist
from images import serializers as image_serializers
from utils.images import image_middleware
from middlewares.middlewares import RequestMiddleware
from images import models as image_models
from permissions import serializers as permission_serializers
from random import randint


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at', 'updated_at']


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        request = self.context.get('request')
        print(request)
        if request:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                print(field_name)
                self.fields.pop(field_name)

class UserAdminSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserAdmin
        fields = ['id', 'is_active', 'token', 'user', 'name', 'email', 'phone', 'image', 'onesignal_id','birth_date' ,'created_at', 'updated_at', 'is_type',]

    def create(self, request):
        user = None
        new_user = None
        if 'password' in self.context['request'].data and self.context['request'].data['password'] != "":
            try:
                check_user = User.objects.get(username=self.context['request'].data['email'])
                raise serializers.ValidationError('Usuário já existe')
            except ObjectDoesNotExist:
                try:
                    user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])   
                    user.set_password(self.context['request'].data['password'])       
                    user.save()
                    new_user = super(UserAdminSerializer, self).create(request)     
                    new_user.user = user
                    new_user.save()
                    return new_user
                except Exception as e:
                    if user is not None:
                        user.delete()
                    if new_user is not None:
                        new_user.delete()
                    raise serializers.ValidationError(str(e))
        else:
            new_user = super(UserAdminSerializer, self).create(request)
            return new_user
    
    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
        
        updated_user = super(UserAdminSerializer, self).update(user, request)
        return updated_user
    
    def get_token(self, request):
        if request.user:
            token = request.user.auth_token
            return str(token)
        else:
            return ""
    
    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['image'] = '' if instance.image == "" or instance.image == None else url_image + instance.image.url
        response['is_type'] = '' if instance.is_type == "" or instance.is_type == None else permission_serializers.UserTypeSerializer(instance.is_type).data
        return response


class UserClientSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserClient
        fields = ['id', 'status', 'token', 'is_active', 'user', 'name', 'trading_name', 'phone_prefix', 'phone', 'email',
                  'taxpayer', 'site', 'address_street', 'address_neighborhood', 'address_number',
                  'address_city', 'address_state', 'address_complement', 'full_address', 'image',
                  'eval_grade', 'eval_total', 'onesignal_id','birth_date' ,'created_at', 'updated_at']

    def create(self, request):
        user = None
        new_user = None
        try:
            check_user = User.objects.get(username=self.context['request'].data['email'])
            raise serializers.ValidationError('Usuário já existe')
        except ObjectDoesNotExist:
            try:
                user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])   
                user.set_password(self.context['request'].data['password'])       
                user.save()
                new_user = super(UserClientSerializer, self).create(request)     
                new_user.user = user
                new_user.save()
                return new_user
            except Exception as e:
                if user is not None:
                    user.delete()
                if new_user is not None:
                    new_user.delete()
                raise serializers.ValidationError(str(e))
    
    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
        
        updated_user = super(UserClientSerializer, self).update(user, request)
        return updated_user

    def get_token(self, request):
        if request.user:
            token = request.user.auth_token
            return str(token)
        else:
            return ""
    
    # def to_representation(self, instance):
    #     custom_request = RequestMiddleware(get_response=None)
    #     custom_request = custom_request.thread_local.current_request
    #     url_image = 'https://' + custom_request.META['HTTP_HOST']
        
    #     response = super().to_representation(instance)
    #     response['image'] = '' if instance.image == "" or instance.image == None else url_image + instance.image.url
    #     return response
class UserClientWithoutTokenSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserClient
        fields = ['id', 'status', 'is_active', 'user', 'name', 'trading_name', 'phone_prefix', 'phone', 'email',
                  'taxpayer', 'site', 'address_street', 'address_neighborhood', 'address_number',
                  'address_city', 'address_state', 'address_complement', 'full_address', 'image',
                  'eval_grade', 'eval_total', 'onesignal_id','birth_date' ,'created_at', 'updated_at']

    def create(self, request):
        user = None
        new_user = None
        try:
            check_user = User.objects.get(username=self.context['request'].data['email'])
            raise serializers.ValidationError('Usuário já existe')
        except ObjectDoesNotExist:
            try:
                user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])   
                user.set_password(self.context['request'].data['password'])       
                user.save()
                new_user = super(UserClientSerializer, self).create(request)     
                new_user.user = user
                new_user.save()
                return new_user
            except Exception as e:
                if user is not None:
                    user.delete()
                if new_user is not None:
                    new_user.delete()
                raise serializers.ValidationError(str(e))
    
    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
        
        updated_user = super(UserClientSerializer, self).update(user, request)
        return updated_user

    # def get_token(self, request):
    #     if request.user:
    #         token = request.user.auth_token
    #         return str(token)
    #     else:
    #         return ""
    
    # def to_representation(self, instance):
    #     custom_request = RequestMiddleware(get_response=None)
    #     custom_request = custom_request.thread_local.current_request
    #     url_image = 'https://' + custom_request.META['HTTP_HOST']
        
    #     response = super().to_representation(instance)
    #     response['image'] = '' if instance.image == "" or instance.image == None else url_image + instance.image.url
    #     return response

class RecurringPaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPaymentType
        fields = ['id', 'name', 'type', 'quantity']

class UserArtistSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)
    # recurring_payment_type = RecurringPaymentTypeSerializer()

    class Meta:
        model = UserArtist
        fields = ['id', 'token', 'first_login', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
                  'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
                  'address_number', 'address_city', 'address_state', 'address_complement', 'full_address', 
                  'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image', 'expiration_date',
                  'eval_grade', 'eval_total', 'onesignal_id', 'monthly_fee', 'created_at', 'birth_date', 'recurring_payment_type', 'updated_at', 'approved_at', 'photos']
    
    def create(self, request):
        user = None
        new_user = None       
        new_album = None
        password = None
        images_list = []
        try:
            check_user = User.objects.get(username=self.context['request'].data['email'])
            raise serializers.ValidationError('Usuário já existe')
        except ObjectDoesNotExist:
            try:
                user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])
                if 'password' in self.context['request'].data and self.context['request'].data['password'] != "":
                    password = self.context['request'].data['password'] 
                    user.set_password(password)       
                    user.save()
                else:
                    password = User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
                    user.set_password(password)       
                    user.save()

                user.save()


                def random_with_N_digits(n):
                    range_start = 10**(n-1)
                    range_end = (10**n)-1
                    return randint(range_start, range_end)
                new_user = super(UserArtistSerializer, self).create(request)     
                new_user.user = user
                new_user.nick_name = 'GC - {}{}'.format(random_with_N_digits(2),new_user.id)
                new_user.save()
                if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
                    images = self.context['request'].data['images']
                    for image in images:
                        new_photo = image_models.PhotoAlbum(artist=new_user, image=image)
                        new_photo.save()
                        images_list.append(new_photo)

                return new_user
            except Exception as e:
                if user is not None:
                    user.delete()
                if new_user is not None:
                    new_user.delete()
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError(str(e))
    
    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistSerializer, self).update(user, request)
        return updated_user

    def get_token(self, request):
        if request.user:
            token = request.user.auth_token
            return str(token)
        else:
            return ""
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        list_actived_photos = []
        
        for _photo in response["photos"]:
            if _photo["disabled"] == False:
                list_actived_photos.append(_photo) 
        
        if response["recurring_payment_type"] is not None:
            try:
                queryset = RecurringPaymentType.objects.get(id=response["recurring_payment_type"])
                serializer = RecurringPaymentTypeSerializer(queryset).data
                response["recurring_payment_type"] = serializer
            except Exception as e:
                response["recurring_payment_type"] = None


        response["photos"] = list_actived_photos
        return response

class UserArtistLandingPageSerializer(serializers.ModelSerializer):
    # photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)
    # recurring_payment_type = RecurringPaymentTypeSerializer()

    class Meta:
        model = UserArtist
        fields = ['id', 'name', 'image']
    
        # fields = ['id', 'code', 'status', 'name', 'nick_name', 'birthdate',
        #           'gender', 'address_city', 'address_state','hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image',
        #           'eval_grade', 'eval_total', 'monthly_fee', 'created_at', 'birth_date', 'updated_at', 'approved_at', 'photos']
    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     list_actived_photos = []
        
    #     for _photo in response["photos"]:
    #         if _photo["disabled"] == False:
    #             list_actived_photos.append(_photo) 

    #     response["photos"] = list_actived_photos
    #     return response

class UserArtistWithoutTokenAndPhotoSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    # photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = UserArtist
        fields = ['id', 'first_login', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
                  'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
                  'address_number', 'address_city', 'address_state', 'address_complement', 'full_address', 
                  'hair', 'eye', 'skin', 'stature', 'waist', 'monthly_fee', 'hip', 'bust', 'image',
                  'eval_grade', 'eval_total', 'onesignal_id', 'created_at', 'birth_date','updated_at', 'approved_at']
    
    def create(self, request):
        user = None
        new_user = None       
        new_album = None
        password = None
        images_list = []
        try:
            check_user = User.objects.get(username=self.context['request'].data['email'])
            raise serializers.ValidationError('Usuário já existe')
        except ObjectDoesNotExist:
            try:
                user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])
                if 'password' in self.context['request'].data and self.context['request'].data['password'] != "":
                    password = self.context['request'].data['password'] 
                    user.set_password(password)       
                    user.save()
                else:
                    password = User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
                    user.set_password(password)       
                    user.save()

                user.save()


                def random_with_N_digits(n):
                    range_start = 10**(n-1)
                    range_end = (10**n)-1
                    return randint(range_start, range_end)
                new_user = super(UserArtistSerializer, self).create(request)     
                new_user.user = user
                new_user.nick_name = 'GC - {}{}'.format(random_with_N_digits(2),new_user.id)
                new_user.save()
                if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
                    images = self.context['request'].data['images']
                    for image in images:
                        new_photo = image_models.PhotoAlbum(artist=new_user, image=image)
                        new_photo.save()
                        images_list.append(new_photo)

                return new_user
            except Exception as e:
                if user is not None:
                    user.delete()
                if new_user is not None:
                    new_user.delete()
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError(str(e))
    
    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistSerializer, self).update(user, request)
        return updated_user

    # def get_token(self, request):
    #     if request.user:
    #         token = request.user.auth_token
    #         return str(token)
    #     else:
    #         return ""
    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     list_actived_photos = []
    #     for _photo in response["photos"]:
    #         if _photo["disabled"] == False:
    #             list_actived_photos.append(_photo) 
        
    #     response["photos"] = list_actived_photos
    #     return response


class EvaluationClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationClient
        fields = ['id', 'hide', 'invite', 'evaluator', 'rated', 'grade', 'description', 'tag', 'created_at', 'updated_at']

    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['evaluator'] = '' if instance.evaluator == "" or instance.evaluator == None else UserClientSerializer(instance.evaluator).data
        response['rated'] = '' if instance.rated == "" or instance.rated == None else UserArtistWithoutTokenAndPhotoSerializer(instance.rated).data

        return response

class EvaluationArtistSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField('get_tags', read_only=True)
    class Meta:
        model = EvaluationArtist
        fields = ['id', 'hide', 'invite', 'evaluator', 'rated', 'grade', 'description', 'tag', 'tags', 'created_at', 'updated_at']
    
    def get_tags(self, request):
        tags = request.tag.all()
        list_tags = []
        if len(tags)> 0:
            for tag in tags:
                obj = {
                    'id':tag.id,
                    'name': tag.name
                }
                list_tags.append(obj)
        else:
            pass
        return list_tags
    
    def to_representation(self, instance):
        custom_request = RequestMiddleware(get_response=None)
        custom_request = custom_request.thread_local.current_request
        url_image = 'https://' + custom_request.META['HTTP_HOST']
        
        response = super().to_representation(instance)
        response['evaluator'] = '' if instance.evaluator == "" or instance.evaluator == None else UserArtistWithoutTokenAndPhotoSerializer(instance.evaluator).data
        response['rated'] = '' if instance.rated == "" or instance.rated == None else UserClientSerializer(instance.rated).data


        return response

class UserArtistPhotosValidSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = UserArtist
        fields = ['id', 'first_login', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
                  'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
                  'address_number', 'address_city', 'address_state', 'address_complement', 'full_address', 
                  'hair', 'eye', 'skin', 'stature', 'waist', 'expiration_date', 'recurring_payment_type', 'monthly_fee', 'hip', 'bust', 'image',
                  'eval_grade', 'eval_total', 'onesignal_id', 'created_at', 'birth_date','updated_at', 'approved_at', 'photos', 'token']

    def get_token(self, request):
        if request.user:
            token = request.user.auth_token
            return str(token)
        else:
            return ""

    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistPhotosValidSerializer, self).update(user, request)
        return updated_user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        list_actived_photos = []
        for _photo in response["photos"]:
            if _photo["is_active"] == True and _photo["disabled"] == False:
                list_actived_photos.append(_photo) 
        
        response["photos"] = list_actived_photos
        return response

class UserArtistOnlyPhotosValidSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = UserArtist
        fields = ['id', 'first_login', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
                  'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
                  'address_number', 'address_city', 'monthly_fee', 'address_state', 'address_complement', 'full_address', 
                  'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image', 'expiration_date',
                  'eval_grade', 'eval_total', 'onesignal_id', 'created_at', 'birth_date','updated_at', 'approved_at', 'photos']

    # def get_token(self, request):
    #     if request.user:
    #         token = request.user.auth_token
    #         return str(token)
    #     else:
    #         return ""

    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistPhotosValidSerializer, self).update(user, request)
        return updated_user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        list_actived_photos = []
        for _photo in response["photos"]:
            if _photo["is_active"] == True and _photo["disabled"] == False:
                list_actived_photos.append(_photo) 
        
        response["photos"] = list_actived_photos
        return response
class UserArtistWithoutTokenSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    # photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = UserArtist
        fields = ['id', 'first_login', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
                  'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
                  'address_number', 'address_city', 'monthly_fee', 'address_state', 'address_complement', 'full_address', 
                  'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image',
                  'eval_grade', 'eval_total', 'onesignal_id', 'created_at', 'birth_date','updated_at', 'approved_at']

    # def get_token(self, request):
    #     if request.user:
    #         token = request.user.auth_token
    #         return str(token)
    #     else:
    #         return ""

    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistPhotosValidSerializer, self).update(user, request)
        return updated_user

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     list_actived_photos = []
    #     for _photo in response["photos"]:
    #         if _photo["is_active"] == True and _photo["disabled"] == False:
    #             list_actived_photos.append(_photo) 
        
    #     response["photos"] = list_actived_photos
    #     return response

class UserArtistApprovedSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    photos = serializers.SerializerMethodField()
    # photos = image_serializers.PhotoAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = UserArtist
        fields = ['id', 'name', 'image', 'photos', 'email']
        # fields = ['id', 'code', 'status', 'user', 'name', 'nick_name', 'birthdate', 'phone_prefix', 'phone',
        #           'taxpayer', 'email', 'gender', 'instagram', 'address_street', 'address_neighborhood', 
        #           'address_number', 'address_city', 'address_state', 'address_complement', 'full_address', 
        #           'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image',
        #           'eval_grade', 'eval_total', 'onesignal_id', 'created_at', 'birth_date','updated_at', 'approved_at', 'photos']

    # def get_token(self, request):
    #     if request.user:
    #         token = request.user.auth_token
    #         return str(token)
    #     else:
    #         return ""

    def get_photos(self, request):
        return []

    def update(self, user, request):
        context = self.context['request'].data
        if 'password' in context:
            password = context['password']
            user.user.set_password(password)
            user.user.save()
            
        if 'email' in context:
            email = context['email']
            try:
                check_if_my_email = User.objects.get(id=user.user.id).email
                if check_if_my_email != email:
                    check_user = User.objects.get(email=email)
                    raise serializers.ValidationError("E-mail já está sendo utilizado")
            except ObjectDoesNotExist:
                user.user.email = email
                user.user.username = email
                user.user.save()
                user.email = email
                user.save()
            
        if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
            images_list = []
            try:
                images = self.context['request'].data['images']
                for image in images:
                    new_photo = image_models.PhotoAlbum(artist=user, image=image)
                    new_photo.save()
                    images_list.append(new_photo)
            except Exception as e:
                if len(images_list) > 0:
                    for img in images_list:
                        img.delete()
                raise serializers.ValidationError("Erro ao salvar imagens")
        
        updated_user = super(UserArtistPhotosValidSerializer, self).update(user, request)
        return updated_user

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     list_actived_photos = []
    #     for _photo in response["photos"]:
    #         if _photo["is_active"] == True and _photo["disabled"] == False:
    #             list_actived_photos.append(_photo) 
        
    #     response["photos"] = list_actived_photos
    #     return response