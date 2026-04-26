from django.db import models
from datetime import date

class EducationLevel(models.Model):

    id = models.AutoField(unique=True, verbose_name="ID", primary_key=True)
    code = models.IntegerField(unique=True, verbose_name="Code of Education Leval")
    description = models.CharField(max_length= 100, verbose_name="Description")

    def __str__(self):
        return self.description
    

class Collaborator(models.Model):

    id = models.AutoField(unique=True, verbose_name="id",primary_key=True)
    date_of_birth = models.DateField(verbose_name="Date of birth")
    service_years = models.IntegerField(verbose_name="Service times in years")
    work_distance = models.IntegerField(verbose_name="Distance from Residence to Work")


    education_level = models.ForeignKey(
        EducationLevel,
        on_delete= models.PROTECT,
        verbose_name="Education level"
    )

    @property
    def age(self):
        #Calcula a idade do colaborador com base na data de nascimento
        
        now = date.today()
        birthday_has_passed = (now.month, now.day) >= (self.data_of_birth.month, self.data_of_birth.month.day)
        years = now.year - self.date_of_birth.year
        return years if birthday_has_passed else years - 1
    
    def __str__(self):
        return f"Colaborador {self.id} - {self.education_level.description}"
    
class HealthProfile(models.Model):
    collaborator = models.ForeignKey(
        Collaborator,
        on_delete= models.CASCADE,
        related_name='health_profile'
    )
    id = models.AutoField(unique=True, primary_key=True)
    weight = models.FloatField(verbose_name="Weight in Kg")
    height = models.FloatField(verbose_name="Height in cm")
    bmi = models.FloatField(verbose_name="Body Mass Index", null=True, blank=True)
    social_drinker = models.BooleanField(default=False, verbose_name="Social drinker")
    social_smoker = models.BooleanField(default=False, verbose_name="Social smoker")

    def save(self, *args, **kwargs):
        if self.weight and self.height:
            height_in_meters = self.height / 100
            self.bmi = round(self.weight / (height_in_meters**2), 2)

        super().save(*args,**kwargs)

    def __str__(self):
        return f"Health - Collaborator {self.collaborator.id}"
    
class FamiliarProfile(models.Model):
    collaborator = models.ForeignKey(
        Collaborator,
        on_delete=models.CASCADE,
        related_name="familiar_profile"
    )
    id = models.AutoField(unique=True, primary_key=True)
    sons = models.IntegerField(default=0, verbose_name="Quantity of sons")
    pets = models.IntegerField(default=0, verbose_name="Quantity os pets")

    def __str__(self):
        return f"Family - Collaborator {self.collaborator.id}"