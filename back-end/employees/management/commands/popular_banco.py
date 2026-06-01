import random
import os
import pandas as pd
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

# Importações dos models de Employees
from employees.models import Collaborator, EducationLevel, HealthProfile, FamiliarProfile

# Importações exatas dos models de Absenteeism
from absenteeism.models import ReasonAbsenteeism, MonthlyContext, AbsenteeismRegister

from accounts.models import User

class Command(BaseCommand):
    help = 'Populates the database using realistic data from the CSV combined with synthetic names'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting data ingestion using DEMO CSV. This might take a few seconds..."))

        try:
            target_manager = User.objects.get(username='carvalhosannyer')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'carvalhosannyer' not found. Please create it first."))
            return

        csv_path = os.path.join(settings.BASE_DIR, 'machine_learning_models', 'data', 'Dialgah_Dados_Teste_DEMO.csv')
        
        try:
            df = pd.read_csv(csv_path, sep=';', decimal=',')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_path}"))
            return

        # Amostra de 50 linhas aleatórias do CSV
        df_sample = df.sample(n=50, replace=False).reset_index(drop=True)

        # Listas para gerar nomes aleatórios
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "Sannyer", "Fani", "Klisman"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Cardoso", "Souza"]

        # 1. Create Education Levels
        levels = ["High School", "Graduate", "Postgraduate", "Master / Doctor"]
        objs_levels = []
        for i, desc in enumerate(levels, start=1):
            level, _ = EducationLevel.objects.get_or_create(code=i, defaults={'description': desc})
            objs_levels.append(level)
        
        self.stdout.write("✅ Education Levels ready.")

        # 2. Create Absenteeism Reasons
        reasons_data = [
            (0, "Certain infectious and parasitic diseases"),
            (1, "Neoplasms"),
            (2, "Diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism"),
            (3, "Endocrine, nutritional and metabolic diseases"),
            (4, "Mental and behavioural disorders"),
            (5, "Diseases of the nervous system"),
            (6, "Diseases of the eye and adnexa"),
            (7, "Diseases of the ear and mastoid process"),
            (8, "Diseases of the circulatory system"),
            (9, "Diseases of the respiratory system"),
            (10, "Diseases of the digestive system"),
            (11, "Diseases of the skin and subcutaneous tissue"),
            (12, "Diseases of the musculoskeletal system and connective tissue"),
            (13, "Diseases of the genitourinary system"),
            (14, "Pregnancy, childbirth and the puerperium"),
            (15, "Certain conditions originating in the perinatal period"),
            (16, "Congenital malformations, deformations and chromosomal abnormalities"),
            (17, "Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified"),
            (18, "Injury, poisoning and certain other consequences of external causes"),
            (19, "External causes of morbidity and mortality"),
            (20, "Factors influencing health status and contact with health services."),
            (21, "patient follow-up"),
            (22, "medical consultation"),
            (23, "blood donation"),
            (24, "laboratory examination"),
            (25, "unjustified absence"),
            (26, "physiotherapy"),
            (27, "dental consultation"),
        ]
        
        for code, desc in reasons_data:
            ReasonAbsenteeism.objects.update_or_create(code=code, defaults={'description': desc})
        
        self.stdout.write("✅ Absenteeism Reasons ready.")

        # Limpeza para evitar duplicação em execuções sucessivas
        Collaborator.objects.all().delete()
        AbsenteeismRegister.objects.all().delete()

        created_collaborators = []
        
        # Vamos definir que exatamente os primeiros 15 do loop serão do manager
        # ou podemos fazer um random.sample dos indices
        manager_indices = set(random.sample(range(50), 15))

        for idx, row in df_sample.iterrows():
            # ... (rest of collaborator creation)
            nome_completo = f"{random.choice(first_names)} {random.choice(last_names)}"
            # Calcula data de nascimento a partir da idade do CSV
            age = int(row['Age'])
            data_nasc = date.today() - timedelta(days=age * 365.25)
            
            # Dados Reais do CSV para o Colaborador
            service_years = int(row['Service time'])
            work_distance = int(row['Distance from Residence to Work'])
            
            # Atribui o manager para ~15 colaboradores
            assigned_manager = target_manager if idx in manager_indices else None
            
            colab = Collaborator.objects.create(
                full_name=nome_completo,
                date_of_birth=data_nasc,
                service_years=service_years,
                work_distance=work_distance,
                education_level=random.choice(objs_levels),
                manager=assigned_manager
            )
            created_collaborators.append(colab)

            # Health Profile do CSV
            # 'Body mass index', 'Social drinker', 'Social smoker'
            bmi = float(row['Body mass index'])
            # Estimativa simples de altura/peso baseada no BMI para manter o modelo coerente
            # Assumindo altura de 1.70m
            height = 170.0
            weight = round(bmi * ((height/100)**2), 2)
            
            HealthProfile.objects.create(
                collaborator=colab,
                weight=weight,
                height=height,
                social_drinker=bool(row['Social drinker']),
                social_smoker=bool(row['Social smoker'])
            )
            
            # Familiar Profile do CSV
            # 'Son', 'Pet'
            FamiliarProfile.objects.create(
                collaborator=colab,
                sons=int(row['Son']),
                pets=int(row['Pet'])
            )

            # --- Cria o registro de absenteísmo baseado na linha ---
            
            # Motivo
            reason_code = int(row['Reason for absence'])
            try:
                reason = ReasonAbsenteeism.objects.get(code=reason_code)
            except ReasonAbsenteeism.DoesNotExist:
                # Fallback caso venha um código fora do 0-27 no CSV
                reason, _ = ReasonAbsenteeism.objects.get_or_create(
                    code=reason_code, 
                    defaults={'description': f"Encoded Reason {reason_code}"}
                )

            # Contexto Mensal
            month = int(row['Month of absence'])
            # Algumas linhas tem mes 0 no CSV original (erro comum de dados), ajustando para 1
            if month == 0: month = 1 
            
            context, _ = MonthlyContext.objects.get_or_create(
                month_reference=month,
                year_reference=date.today().year,
                defaults={
                    'work_load_average': float(row['Work load Average/day ']),
                    'hit_target': int(row['Hit target'])
                }
            )

            # Registro Final
            AbsenteeismRegister.objects.create(
                collaborator=colab,
                reason=reason,
                monthly_context=context,
                week_day=int(row['Day of the week']),
                season=int(row['Seasons']),
                transportation_expense=float(row['Transportation expense']),
                disciplinary_failure=bool(row['Disciplinary failure']),
                absenteeism_time=float(row['Gabarito_Horas_Falta'])
            )

        self.stdout.write(f"✅ 50 Collaborators and their realistic records created.")
        self.stdout.write(self.style.SUCCESS('🎉 DATABASE POPULATED SUCCESSFULLY WITH HYBRID DATA!'))