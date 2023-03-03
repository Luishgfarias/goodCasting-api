from rest_framework import routers

from django.urls import path, include

from .views import PlanViewSet, CurrencyViewSet

router = routers.SimpleRouter()

router.register('v1/financial/plan', PlanViewSet)
router.register('v1/financial/currency', CurrencyViewSet)

urlpatterns = router.urls

