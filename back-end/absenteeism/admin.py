from django.contrib import admin
from .models import ReasonAbsenteeism, MonthlyContext, AbsenteeismRegister

@admin.register(ReasonAbsenteeism)
class ReasonAbsenteeismAdmin(admin.ModelAdmin):
    list_display = ('id','code', 'description')
    search_fields = ('description', 'code')

@admin.register(MonthlyContext)
class MonthlyContextAdmin(admin.ModelAdmin):
    list_display = ("month_reference","year_reference","work_load_average","hit_target")
    list_filter = ("year_reference", "month_reference")

@admin.register(AbsenteeismRegister)
class AbsenteeismRegisterAdmin(admin.ModelAdmin):
    list_display = ("collaborator", "reason", "monthly_context", "absenteeism_time", "disciplinary_failure")
    list_filter = ("disciplinary_failure", "week_day","season","reason")
    search_fields = ('collaborator__id',)
