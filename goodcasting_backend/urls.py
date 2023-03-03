from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from core import views
from users.urls import router as user_urls
from images.urls import router as image_urls
from jobs.urls import router as job_urls
from videos.urls import router as video_urls
from supports.urls import router as suport_urls
from financials.urls import router as financial_urls
from permissions.urls import router as permission_urls

router = routers.DefaultRouter()

router.registry.extend(user_urls.registry)
router.registry.extend(image_urls.registry)
router.registry.extend(job_urls.registry)
router.registry.extend(video_urls.registry)
router.registry.extend(suport_urls.registry)
router.registry.extend(financial_urls.registry)
router.registry.extend(permission_urls.registry)

urlpatterns = [
    path('api/v1/accounts/password_reset/', auth_views.PasswordResetView.as_view(
        html_email_template_name = 'registration/html_password_reset_email.html'
    ), name="password_reset"),
    path('api/v1/accounts/', include('django.contrib.auth.urls')),
    path('policy', TemplateView.as_view(template_name='policy_private.html')),
    path('api/', include(router.urls)),
    path('', include('users.urls')),
    path('', admin.site.urls),
    path('users', views.UserViewSet),
    path('groups', views.GroupViewSet)
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
