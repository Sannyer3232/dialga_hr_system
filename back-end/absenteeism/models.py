from django.db import models
from employees.models import Collaborator

class ReasonAbsenteeism(models.Model):

    id = models.AutoField(primary_key=True, unique=True, verbose_name="Id")
    code = models.IntegerField(unique=True, verbose_name="Reason of Absenteeism")
    description = models.CharField(max_length=150, verbose_name="Description of the reason of absenteeism")

    def __str__(self):
        return f'{self.code} - {self.description}'
    
class MonthlyContext(models.Model):
    MONTH_CHOICES = (
        (1,"Jan"),
        (2,"Fev"),
        (3,"Mar"),
        (4,"Apr"),
        (5,"May"),
        (6,"Jun"),
        (7,"Jul"),
        (8,"Aug"),
        (9,"Sep"),
        (10,"Oct"),
        (11,"Nov"),
        (12,"Dec"),
    )


    month_reference = models.IntegerField(choices=MONTH_CHOICES, verbose_name="Reference month(1-12)")
    year_reference = models.IntegerField(default=2026, verbose_name="Reference year" )
    work_load_average = models.FloatField(verbose_name="Workload Average/day")
    hit_target = models.IntegerField(verbose_name = "Hit target")

    def __str__(self):
        return f"{self.month_reference}/{self.year_reference} - Hit: {self.hit_target}"

class AbsenteeismRegister(models.Model):
    
    class WeekDay(models.IntegerChoices):
        SUNDAY = 1, "Sunday"
        MONDAY = 2, "Monday"
        TUESDAY = 3, "Tuesday"
        WEDNESDAY = 4, "Wednesday"
        THURSDAY = 5, "Thursday"
        Friday = 6, "Friday"
        SATURDAY = 7, "Saturday"
    
    class Seasons(models.IntegerChoices):
        SUMMER = 1, "Summer"
        AUTUMN = 2, "Autumn"
        WINTER = 3, "Winter"
        SPRING = 4, "Spring"
    
    collaborator = models.ForeignKey(Collaborator,
                                     on_delete=models.CASCADE,
                                     related_name="absenteeism")
    reason = models.ForeignKey(ReasonAbsenteeism,
                               on_delete=models.PROTECT,
                               related_name="reason")
    monthly_context = models.ForeignKey(MonthlyContext,
                                        on_delete=models.PROTECT,
                                        related_name="month_context")
    
    week_day = models.IntegerField(choices = WeekDay.choices, verbose_name = "Week Day")
    season = models.IntegerField(choices=Seasons.choices, verbose_name="Season of the year")
    transportation_expense = models.FloatField(verbose_name="Transportation expense")
    disciplinary_failure = models.BooleanField(verbose_name="Disciplinary failure")
    absenteeism_time = models.FloatField(verbose_name="Absenteeism time in Hours")

    def __str__(self):
        return f"Absenteeism of {self.absenteeism_time} hour(s) - {self.collaborator.id}"
    