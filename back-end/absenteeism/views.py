from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
import pandas as pd
import joblib
import numpy as np
import os
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from django.conf import settings
from .service import AbsenteeismPredictor
from .models import AbsenteeismRegister
from django.db.models import Avg
from datetime import date
from employees.models import Collaborator

class ModelMetricsView(APIView):
    @extend_schema(
        summary="Calculate Machine Learning Model Metrics",
        description="Calculates MAE, RMSE, and R2 Score based on a percentage of the demo test data.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "percentage": {"type": "number", "minimum": 1, "maximum": 100}
                },
                "required": ["percentage"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "object",
                        "properties": {
                            "mae": {"type": "number"},
                            "rmse": {"type": "number"},
                            "r2_score": {"type": "number"}
                        }
                    },
                    "scatter_plot_data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "actual": {"type": "number"},
                                "predicted": {"type": "number"}
                            }
                        }
                    }
                }
            },
            400: {"description": "Invalid or missing percentage"},
            500: {"description": "Internal error processing the model"}
        }
    )
    def post(self, request):
        percentage = request.data.get('percentage')
        
        if percentage is None:
            return Response({"error": "Percentage is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            percentage = float(percentage)
            if not (1 <= percentage <= 100):
                return Response({"error": "Percentage must be between 1 and 100"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid percentage value"}, status=status.HTTP_400_BAD_REQUEST)

        # Paths
        base_path = os.path.join(settings.BASE_DIR, 'machine_learning_models')
        model_path = os.path.join(base_path, 'Dialgah_LSTM_Mestre_3.keras')
        scaler_path = os.path.join(base_path, 'Dialgah_Scaler.pkl')
        data_path = os.path.join(base_path, 'data', 'Dialgah_Dados_Teste_DEMO.csv')

        try:
            # Load model and scaler
            model = load_model(model_path)
            scaler = joblib.load(scaler_path)
            
            # Load data
            # Assuming the CSV uses ; as separator and , as decimal separator based on observation
            df = pd.read_csv(data_path, sep=';', decimal=',')
            
            # Use specified percentage of data
            num_rows = int(len(df) * (percentage / 100))
            df_subset = df.head(num_rows)
            
            if df_subset.empty:
                 return Response({"error": "Percentage too low, no data selected"}, status=status.HTTP_400_BAD_REQUEST)

            # Features and Target
            # Target is the last column: Gabarito_Horas_Falta
            X = df_subset.iloc[:, :-1]
            y_true = df_subset.iloc[:, -1]
            
            # Scale features
            X_scaled = scaler.transform(X)
            
            # Reshape for LSTM model: (samples, time_steps, features)
            # The model expects (None, 1, features)
            X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

            # Predict
            y_pred = model.predict(X_reshaped, verbose=0)
            
            # Flatten predictions if they are 2D
            if len(y_pred.shape) > 1 and y_pred.shape[1] == 1:
                y_pred = y_pred.flatten()

            # Metrics
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            
            # Data for scatter plot
            scatter_data = [
                {"actual": float(actual), "predicted": float(pred)}
                for actual, pred in zip(y_true, y_pred)
            ]
            
            return Response({
                "metrics": {
                    "mae": mae,
                    "rmse": rmse,
                    "r2_score": r2
                },
                "scatter_plot_data": scatter_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ManagerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(f"O usuario logado é: {user}")

        # 1. Buscar os colaboradores que pertencem a este gerente
        collaborators = Collaborator.objects.filter(manager=user)

        
        
        if not collaborators.exists():
            return Response({
                "message": "Nenhum colaborador encontrado para este gerente.",
                "history": {"actual_total": 0, "predicted_total": 0},
                "next_month_projection": {"total_estimated_hour": 0}
            })

        # 2. Buscar os registros de absenteísmo APENAS para esses colaboradores
        registers = AbsenteeismRegister.objects.filter(collaborator__in=collaborators)

        predictor = AbsenteeismPredictor()
        
        # --- PARTE 1: HISTÓRICO (Baseado nos registros passados) ---
        actual_total = 0
        predicted_total = 0
        details = []

        for reg in registers:
            actual_total += reg.absenteeism_time

            context_data = {
                'reason_code': reg.reason.code,
                'month': reg.monthly_context.month_reference,
                'day_of_week': reg.week_day,
                'season': reg.season,
                'transport_expense': reg.transportation_expense,
                'work_load': reg.monthly_context.work_load_average,
                'hit_target': reg.monthly_context.hit_target,
                'disciplinary_failure': reg.disciplinary_failure,
            }
            
            prediction = predictor.predict_collaborator(reg.collaborator, context_data)
            predicted_total += prediction

            details.append({
                "collaborator": reg.collaborator.full_name,
                "actual": reg.absenteeism_time,
                "predicted": round(prediction, 2),
                "date": f"{reg.monthly_context.month_reference}/{reg.monthly_context.year_reference}"
            })

        # --- PARTE 2: PROJEÇÃO FUTURA (Baseado em cada colaborador único) ---
        next_month_forecast = 0
        projection_details = []

        today = date.today()
        next_month = today.month + 1 if today.month < 12 else 1

        avg_context = {
            'month': next_month,
            'day_of_week': 3, # Simulamos uma quarta-feira média
            'season': 1, # Ajuste conforme a estação do ano atual
            'work_load': 250.0, 
            'hit_target': 95,
            'transport_expense': 150.0,
            'reason_code': 0, # Consulta médica (mais comum)
            'disciplinary_failure': False
        }

        for colab in collaborators:
            # Calcula uma previsão única por colaborador para o próximo mês
            prediction_next_month = predictor.predict_collaborator(colab, avg_context)
            next_month_forecast += prediction_next_month
            
            projection_details.append({
                "collaborator": colab.full_name,
                "estimated_absence_hours": round(prediction_next_month, 2)
            })

        # --- RESPOSTA FINAL ---
        return Response({
            "history": {
                "actual_total": round(actual_total, 2),
                "predicted_total": round(predicted_total, 2),
                "gap": round(actual_total - predicted_total, 2),
                "details": details
            },
            "next_month_projection": {
                "total_estimated_hour": round(next_month_forecast, 2),
                "details": projection_details
            }
        })


class CollaboratorSimulationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
         summary="Simulate Absenteeism (What-if)",
         description="Simulate a scenario for a specific collaborator by overriding context variables.",
         request={
                "application/json": {
                    "type": "object",
                    "properties": {
                        "collaborator_id": {"type": "integer"},
                        "month": {"type": "integer", "default": 1},
                        "day_of_week": {"type": "integer", "default": 2},
                        "work_load": {"type": "number", "default": 250.0},
                        "hit_target": {"type": "integer", "default": 95},
                        "reason_code": {"type": "integer", "default": 0},
                    },
                    "required": ["collaborator_id"]
                }
            }
        )
    def post(self, request):
        user = request.user
        data = request.data
        colab_id = data.get('collaborator_id')

        try:
            colab = Collaborator.objects.get(id = colab_id, manager = user)
        except Collaborator.DoesNotExist:
            return Response({"error": "Colaborador não encontrado ou você não tem permissão."}, status=404)
        
        predictor = AbsenteeismPredictor()

        simulated_context = {
                'reason_code': data.get('reason_code', 0),
                'month': data.get('month', date.today().month),
                'day_of_week': data.get('day_of_week', 3),
                'season': data.get('season', 1),
                'transport_expense': data.get('transport_expense', 150.0),
                'work_load': data.get('work_load', 250.0),
                'hit_target': data.get('hit_target', 90),
                'disciplinary_failure': data.get('disciplinary_failure', False),
            }
        prediction = predictor.predict_collaborator(colab, simulated_context)

        return Response({
                 "collaborator": colab.full_name,
                 "scenario": simulated_context,
                 "predicted_absence_hours": round(prediction, 2)
             })

