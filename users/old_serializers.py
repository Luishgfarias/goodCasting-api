# from rest_framework import serializers
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# from django.db.models.base import ObjectDoesNotExist
# from django.core.files.base import ContentFile
# from .models import UserClient, UserArtist, ArtistProfile, UserAdmin
# from images import models as image_models

# class UserAdminSerializer(serializers.ModelSerializer):
#     token = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = UserAdmin
#         fields = ['id', 'is_active', 'token', 'user', 'name', 'email', 'phone', 'image','created_at', 'updated_at']

#     def create(self, request):
#         user = None
#         new_user = None
#         try:
#             check_user = User.objects.get(username=self.context['request'].data['email'])
#             raise serializers.ValidationError('Usuário já existe')
#         except ObjectDoesNotExist:
#             try:
#                 user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])   
#                 user.set_password(self.context['request'].data['password'])       
#                 user.save()
#                 new_user = super(UserAdminSerializer, self).create(request)     
#                 new_user.user = user
#                 new_user.save()
#                 return new_user
#             except Exception as e:
#                 if user is not None:
#                     user.delete()
#                 if new_user is not None:
#                     new_user.delete()
#                 raise serializers.ValidationError(str(e))
    
#     def update(self, user, request):
#         context = self.context['request'].data
#         if 'password' in context:
#             password = context['password']
#             user.user.set_password(password)
#             user.user.save()
            
#         if 'email' in context:
#             email = context['email']
#             try:
#                 check_if_my_email = User.objects.get(id=user.user.id).email
#                 if check_if_my_email != email:
#                     check_user = User.objects.get(email=email)
#                     raise serializers.ValidationError("E-mail já está sendo utilizado")
#             except ObjectDoesNotExist:
#                 user.user.email = email
#                 user.user.username = email
#                 user.user.save()
#                 user.email = email
#                 user.save()
        
#         updated_user = super(UserAdminSerializer, self).update(user, request)
#         return updated_user
    
#     def get_token(self, request):
#         if request.user:
#             token = request.user.auth_token
#             return str(token)
#         else:
#             return ""

# class UserClientSerializer(serializers.ModelSerializer):
#     token = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = UserClient
#         fields = ['id', 'token', 'user', 'name', 'trading_name', 'email', 'phone_prefix', 'phone', 'taxpayer', 'site', 'address_street', 'address_number', 'address_neighborhood', 'address_city', 'address_state', 'address_complement', 'full_address',
#                  'image', 'status', 'eval_grade', 'eval_total', 'created_at', 'updated_at']
    
#     def create(self, request):
#         user = None
#         new_user = None
#         try:
#             check_user = User.objects.get(username=self.context['request'].data['email'])
#             raise serializers.ValidationError('Usuário já existe')
#         except ObjectDoesNotExist:
#             try:
#                 user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])   
#                 user.set_password(self.context['request'].data['password'])       
#                 user.save()
#                 new_user = super(UserClientSerializer, self).create(request)     
#                 new_user.user = user
#                 new_user.save()
#                 return new_user
#             except Exception as e:
#                 if user is not None:
#                     user.delete()
#                 if new_user is not None:
#                     new_user.delete()
#                 raise serializers.ValidationError(str(e))
    
#     def update(self, user, request):
#         context = self.context['request'].data
#         if 'password' in context:
#             password = context['password']
#             user.user.set_password(password)
#             user.user.save()
            
#         if 'email' in context:
#             email = context['email']
#             try:
#                 check_if_my_email = User.objects.get(id=user.user.id).email
#                 if check_if_my_email != email:
#                     check_user = User.objects.get(email=email)
#                     raise serializers.ValidationError("E-mail já está sendo utilizado")
#             except ObjectDoesNotExist:
#                 user.user.email = email
#                 user.user.username = email
#                 user.user.save()
#                 user.email = email
#                 user.save()
                
#         if 'status' in context:
#             status = context['status']
#             if status == "APROVADO":
#                 print('Email vai ser enviado')
#                 # Enviar Email/SMS após aprovação
#             user.status = status
#             user.save()
        
#         updated_user = super(UserClientSerializer, self).update(user, request)
#         return updated_user
    
#     def get_token(self, request):
#         if request.user:
#             token = request.user.auth_token
#             return str(token)
#         else:
#             return ""

# class ArtistProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArtistProfile
#         fields = ['id', 'name', 'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'created_at', 'updated_at']

# class UserArtistSerializer(serializers.ModelSerializer):
#     token = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = UserArtist
#         fields = ['id', 'token', 'user', 'first_login', 'code', 'name', 'age', 'email', 'phone_prefix', 'phone', 'birthdate', 'taxpayer', 'instagram', 
#                  'address_street', 'address_number', 'address_neighborhood', 'address_city', 'address_state', 'address_complement', 'full_address', 'city_operation',
#                  'approved_at', 'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'status', 'eval_grade', 'eval_total', 'image', 'created_at', 'updated_at']

#     def create(self, request):
#         user = None
#         new_user = None
#         new_album = None
#         password = None
#         try:
#             check_user = User.objects.get(username=self.context['request'].data['email'])
#             raise serializers.ValidationError('Usuário já existe')
#         except ObjectDoesNotExist:
#             try:
#                 # User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
#                 user = User(username = self.context['request'].data['email'], email = self.context['request'].data['email'])
#                 if 'password' in self.context['request'].data and self.context['request'].data['password'] != "":
#                     password = self.context['request'].data['password'] 
#                     user.set_password(password)       
#                     user.save()
#                 else:
#                     password = User.objects.make_random_password(length=8, allowed_chars='abcdefghjkmnpqrstuvwxyz123456789')
#                     user.set_password(password)       
#                     user.save()
#                 new_user = super(UserArtistSerializer, self).create(request)     
#                 new_user.user = user
#                 new_user.save()
#                 if 'images' in self.context['request'].data and self.context['request'].data['images'] != "":
#                     images = self.context['request'].FILES.getlist('images')
#                     new_album = image_models.ArtistAlbum(artist=new_user)
#                     new_album.save()
#                     for image in list(images):
#                         new_photo = image_models.PhotoAlbum(album=new_album, image=image)
#                         new_photo.save()
#                 return new_user
#             except Exception as e:
#                 if user is not None:
#                     user.delete()
#                 if new_user is not None:
#                     new_user.delete()
#                 if new_album is not None:
#                     new_album.delete()
#                 raise serializers.ValidationError(str(e))
    
#     def update(self, user, request):
#         context = self.context['request'].data
#         if 'password' in context:
#             password = context['password']
#             user.user.set_password(password)
#             user.user.save()

#         if 'images' in context:
#             images = self.context['request'].FILES.getlist('images')
#             for obj in list(images):
#                 album = image.models.ArtistAlbum.objects.get(artist=user)
#                 new_photo = image_models.PhotoAlbum(album=album, image=obj.image, is_active=obj.is_active)
#                 new_photo.save()
        
#         if 'status' in context:
#             status = context['status']
#             if status == "APROVADO":
#                 print('Email será enviado')
#                 # Enviar Email/SMS após aprovação
#             user.status = status
#             user.save()
           
            
#         if 'email' in context:
#             email = context['email']
#             try:
#                 check_if_my_email = User.objects.get(id=user.user.id).email
#                 if check_if_my_email != email:
#                     check_user = User.objects.get(email=email)
#                     raise serializers.ValidationError("E-mail já está sendo utilizado")
#             except ObjectDoesNotExist:
#                 user.user.email = email
#                 user.user.username = email
#                 user.user.save()
#                 user.email = email
#                 user.save()
        
#         updated_user = super(UserArtistSerializer, self).update(user, request)
#         return updated_user
    
#     def get_token(self, request):
#         if request.user:
#             token = request.user.auth_token
#             return str(token)
#         else:
#             return ""