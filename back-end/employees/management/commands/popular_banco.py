import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand

# Importações dos models de Employees
from employees.models import Collaborator, EducationLevel, HealthProfile, FamiliarProfile

# Importações exatas dos models de Absenteeism
from absenteeism.models import ReasonAbsenteeism, MonthlyContext, AbsenteeismRegister

class Command(BaseCommand):
    help = 'Populates the database with new, random data for the HR System'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting data ingestion. This might take a few seconds..."))

        # Listas para gerar nomes aleatórios
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "Sannyer", "Fani", "Klisman"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Cardoso", "Souza"]

        # 1. Create Education Levels
        levels = ["High School", "Graduate", "Postgraduate", "Master / Doctor"]
        objs_levels = []
        for i, desc in enumerate(levels, start=1):
            level, _ = EducationLevel.objects.get_or_create(code=i, defaults={'description': desc})
            objs_levels.append(level)
        self.stdout.write("✅ Education Levels created.")

        # 2. Create Absence Reasons
        objs_reasons = []
        for i in range(0, 29):
            reason, _ = ReasonAbsenteeism.objects.get_or_create(
                code=i, 
                defaults={'description': f"Encoded Reason {i}" if i > 0 else "Medical Consultation"}
            )
            objs_reasons.append(reason)
        self.stdout.write("✅ Absence Reasons created.")

        # 3. Create Monthly Contexts
        objs_contexts = []
        for month in range(1, 13):
            context, _ = MonthlyContext.objects.get_or_create(
                month_reference=month,
                year_reference=2025,
                defaults={
                    'work_load_average': round(random.uniform(200.0, 350.0), 3),
                    'hit_target': random.randint(85, 100)
                }
            )
            objs_contexts.append(context)
        self.stdout.write("✅ Monthly Contexts created.")

        # 4. Create 50 New Collaborators
        Collaborator.objects.all().delete() # Limpa antigos para evitar duplicação
        created_collaborators = []
        
        for _ in range(50):
            idade_aleatoria = random.randint(22, 60)
            data_nasc = date.today() - timedelta(days=idade_aleatoria * 365)
            nome_completo = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            colab = Collaborator.objects.create(
                full_name=nome_completo,
                date_of_birth=data_nasc,
                service_years=random.randint(1, 25),
                work_distance=random.randint(5, 55),
                education_level=random.choice(objs_levels)
            )
            created_collaborators.append(colab)

            # Health Profile
            HealthProfile.objects.create(
                collaborator=colab,
                weight=round(random.uniform(60.0, 105.0), 2),
                height=round(random.uniform(155.0, 195.0), 2),
                social_drinker=random.choice([True, False]),
                social_smoker=random.choice([True, False, False, False]) # 25% chance
            )
            
            # Familiar Profile
            FamiliarProfile.objects.create(
                collaborator=colab,
                sons=random.choice([0, 0, 1, 2, 3]),
                pets=random.choice([0, 1, 2])
            )
        self.stdout.write(f"✅ {len(created_collaborators)} Collaborators created with Profiles.")

        # 5. Create 500 Absence Records
        AbsenteeismRegister.objects.all().delete()
        for _ in range(500):
            AbsenteeismRegister.objects.create(
                collaborator=random.choice(created_collaborators),
                reason=random.choice(objs_reasons),
                monthly_context=random.choice(objs_contexts),
                week_day=random.randint(2, 6),
                season=random.randint(1, 4),
                transportation_expense=round(random.uniform(118.0, 388.0), 2),
                disciplinary_failure=random.choices([True, False], weights=[0.05, 0.95])[0],
                absenteeism_time=random.choice([1.0, 2.0, 3.0, 4.0, 8.0, 16.0, 24.0])
            )
        self.stdout.write("✅ 500 Absence Records created.")

        self.stdout.write(self.style.SUCCESS('🎉 DATABASE POPULATED SUCCESSFULLY!'))