from rest_framework import routers

from django.urls import path, include

from .views import SolicitationViewSet, CategoryViewSet, SolicitationInviteViewSet, ArtistProfileViewSet
from .charts import SolicitationChartViewSet

router = routers.SimpleRouter()

router.register('v1/job/solicitation', SolicitationViewSet)
router.register('v1/job/invite/solicitation', SolicitationInviteViewSet)
router.register('v1/job/category', CategoryViewSet)
router.register('v1/job/profile', ArtistProfileViewSet)
router.register('v1/chart', SolicitationChartViewSet, basename='chart-job')

urlpatterns = router.urls

