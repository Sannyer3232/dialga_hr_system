from django.contrib import admin
from .models import EducationLevel, Collaborator, HealthProfile, FamiliarProfile

class HealthProfileInline(admin.StackedInline):
    model = HealthProfile
    can_delete = False
    verbose_name_plural = "Health Profile"

class FamiliarProgileInLine(admin.StackedInline):
    model = FamiliarProfile
    can_delete = False
    verbose_name_plural = "Familiar Profile"

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('id','age','education_level','date_of_birth', 'service_years', 'work_distance')
    search_fields = ('id',)
    list_filter = ('education_level',)
    inlines = [HealthProfileInline, FamiliarProgileInLine]

@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('id','description',)