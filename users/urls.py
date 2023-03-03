from rest_framework import routers

from django.urls import path, include

from .views import RecurringPaymentTypeViewSet, TagViewSet, UserAdminViewSet, UserClientViewSet, UserArtistViewSet, EvaluationClientViewSet, EvaluationArtistViewSet
from .authentications import UserClientAuthentication, UserAdminAuthentication, UserArtistAuthentication, CheckUserLogged, CheckUserEmail
from .charts import UserClientChartViewSet, UserArtistChartViewSet

router = routers.SimpleRouter()

router.register('v1/user/admin', UserAdminViewSet)
router.register('v1/user/client', UserClientViewSet)
router.register('v1/user/artist', UserArtistViewSet)
router.register('v1/user/evaluation/client', EvaluationClientViewSet)
router.register('v1/user/evaluation/artist', EvaluationArtistViewSet)
router.register('v1/user/evaluation/tag', TagViewSet)
router.register('v1/recurring-payment-type', RecurringPaymentTypeViewSet)
router.register('v1/chart', UserClientChartViewSet, basename='chart-client')
router.register('v1/chart', UserArtistChartViewSet, basename='chart-artist')
router.register('v1/session', CheckUserLogged, basename='logged')
router.register('v1', CheckUserEmail, basename='validation')


urlpatterns = [
  path('api/v1/client/authentication/', UserClientAuthentication.as_view()),
  path('api/v1/artist/authentication/', UserArtistAuthentication.as_view()),
  path('api/v1/admin/authentication/', UserAdminAuthentication.as_view()),

]
