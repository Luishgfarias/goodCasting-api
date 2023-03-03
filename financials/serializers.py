from rest_framework import serializers
from .models import Plan, CurrencyPlan

class PlanSerializer(serializers.ModelSerializer):
  class Meta:
    model = Plan
    fields = '__all__'

class CurrencyPlanSerializer(serializers.ModelSerializer):
  class Meta:
    model = CurrencyPlan
    fields = '__all__'