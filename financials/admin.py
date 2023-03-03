from django.contrib import admin

from .models import Plan, CurrencyPlan

class PlanAdmin(admin.ModelAdmin):
  pass

class CurrencyPlanAdmin(admin.ModelAdmin):
  pass

admin.site.register(Plan, PlanAdmin)
admin.site.register(CurrencyPlan, CurrencyPlanAdmin)