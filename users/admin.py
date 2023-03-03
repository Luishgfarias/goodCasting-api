from django.contrib import admin

from .models import Tag, UserAdmin, UserArtist, UserClient, EvaluationClient, EvaluationArtist, RecurringPaymentType

class TagAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Avaliação Cliente', {'fields': ['name', 'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class EvaluationClientAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Avaliação Cliente', {'fields': ['hide', 'invite', 'evaluator', 'rated', 'grade', 'description', 'tag', 'created_at',
                                          'updated_at']})
    ]

    list_display = ['id', 'rated', 'grade', 'hide']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class EvaluationArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Avaliação Artista', {'fields': ['hide', 'invite', 'evaluator', 'rated', 'grade', 'description', 'tag', 'created_at',
                                          'updated_at']})
    ]

    list_display = ['id', 'rated', 'grade', 'hide']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class UserAdminAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Admin', {'fields': ['is_active', 'is_type', 'user', 'name', 'email', 'phone', 'image', 'onesignal_id','birth_date' ,'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name', 'email', 'phone', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class UserClientAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Cliente', {'fields': ['status', 'user', 'name', 'trading_name', 'phone_prefix', 'phone', 'email',
                                'taxpayer', 'site', 'address_street', 'address_neighborhood', 'address_number',
                                'address_city', 'address_state', 'address_complement', 'full_address', 'image','is_active',
                                'eval_grade', 'eval_total', 'onesignal_id','birth_date' ,'created_at', 'updated_at']})
    ]

    list_display = ['id', 'name', 'email', 'phone', 'status', 'onesignal_id']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

class UserArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Cliente', {'fields': ['status', 'first_login', 'code', 'recurring_payment_type', 'user', 'name', 'nick_name', 'age', 'gender', 'birthdate', 'phone_prefix', 'phone',
                                'taxpayer', 'email', 'instagram', 'expiration_date', 'address_street', 'address_neighborhood', 
                                'address_number', 'address_city', 'address_state', 'address_complement', 'full_address', 
                                'hair', 'eye', 'skin', 'stature', 'waist', 'hip', 'bust', 'image',
                                'eval_grade', 'eval_total', 'onesignal_id', 'birth_date', 'monthly_fee', 'created_at', 'updated_at', 'approved_at',]})
    ]

    list_display = ['id', 'name', 'email', 'phone', 'status', 'onesignal_id']
    readonly_fields = ['created_at', 'updated_at', 'code']
    list_per_page = 30

class RecurringPaymentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'quantity','type']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

admin.site.register(Tag, TagAdmin)
admin.site.register(UserClient, UserClientAdmin)
admin.site.register(UserAdmin, UserAdminAdmin)
admin.site.register(UserArtist, UserArtistAdmin)
admin.site.register(EvaluationClient, EvaluationClientAdmin)
admin.site.register(EvaluationArtist, EvaluationArtistAdmin)
admin.site.register(RecurringPaymentType, RecurringPaymentTypeAdmin)