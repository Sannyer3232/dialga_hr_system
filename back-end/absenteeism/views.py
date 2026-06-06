from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
import pandas as pd
import joblib
import numpy as np
import os
import time
from datetime import date
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from django.conf import settings
from .service import AbsenteeismPredictor
from .models import AbsenteeismRegister, ReasonAbsenteeism
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
            df = pd.read_csv(data_path, sep=';', decimal=',')
            
            # Use specified percentage of data
            num_rows = int(len(df) * (percentage / 100))
            df_subset = df.head(num_rows)
            
            if df_subset.empty:
                 return Response({"error": "Percentage too low, no data selected"}, status=status.HTTP_400_BAD_REQUEST)

            # Features and Target
            X = df_subset.iloc[:, :-1]
            y_true = df_subset.iloc[:, -1]
            
            # Scale features
            X_scaled = scaler.transform(X)
            
            # Reshape for LSTM model: (samples, time_steps, features)
            X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

            # Predict
            y_pred = model.predict(X_reshaped, verbose=0)
            
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

    def get_dashboard_data(self, user, custom_context=None):
        collaborators = Collaborator.objects.filter(manager=user)
        
        if not collaborators.exists():
            return {
                "message": "Nenhum colaborador encontrado para este gerente.",
                "current_month": {"actual_total": 0, "predicted_total": 0, "gap": 0},
                "next_month": {"total_estimated_hour": 0, "month_reference": 0, "year_reference": 0, "details": []},
                "history": {"details": []}
            }

        today = date.today()
        current_month = today.month
        current_year = today.year
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = current_year if today.month < 12 else current_year + 1

        predictor = AbsenteeismPredictor()
        
        # --- 1. MÊS ATUAL: REAL VS PREVISTO ---
        current_registers = AbsenteeismRegister.objects.filter(
            collaborator__in=collaborators,
            monthly_context__month_reference=current_month,
            monthly_context__year_reference=current_year
        )

        actual_current_total = 0
        predicted_current_total = 0

        for reg in current_registers:
            actual_current_total += reg.absenteeism_time
            
            if custom_context:
                ctx = {
                    'reason_code': custom_context.get('reason_code', reg.reason.code),
                    'month': current_month,
                    'day_of_week': custom_context.get('day_of_week', reg.week_day),
                    'season': reg.season,
                    'transport_expense': reg.transportation_expense,
                    'work_load': custom_context.get('work_load', reg.monthly_context.work_load_average),
                    'hit_target': custom_context.get('hit_target', reg.monthly_context.hit_target),
                    'disciplinary_failure': custom_context.get('disciplinary_failure', reg.disciplinary_failure),
                }
            else:
                ctx = {
                    'reason_code': reg.reason.code,
                    'month': reg.monthly_context.month_reference,
                    'day_of_week': reg.week_day,
                    'season': reg.season,
                    'transport_expense': reg.transportation_expense,
                    'work_load': reg.monthly_context.work_load_average,
                    'hit_target': reg.monthly_context.hit_target,
                    'disciplinary_failure': reg.disciplinary_failure,
                }
            
            predicted_current_total += predictor.predict_collaborator(reg.collaborator, ctx)

        # --- 2. PRÓXIMO MÊS: PROJEÇÃO ---
        next_month_forecast = 0
        projection_details = []

        default_next_ctx = {
            'month': next_month,
            'day_of_week': custom_context.get('day_of_week', 3) if custom_context else 3,
            'season': 1,
            'work_load': custom_context.get('work_load', 250.0) if custom_context else 250.0,
            'hit_target': custom_context.get('hit_target', 95) if custom_context else 95,
            'transport_expense': 150.0,
            'reason_code': custom_context.get('reason_code', 0) if custom_context else 0,
            'disciplinary_failure': custom_context.get('disciplinary_failure', False) if custom_context else False
        }

        for colab in collaborators:
            pred_next = predictor.predict_collaborator(colab, default_next_ctx)
            next_month_forecast += pred_next
            projection_details.append({
                "collaborator": colab.full_name,
                "estimated_absence_hours": round(pred_next, 2)
            })

        # --- 3. HISTÓRICO GERAL ---
        all_registers = AbsenteeismRegister.objects.filter(collaborator__in=collaborators).order_by('monthly_context__year_reference', 'monthly_context__month_reference')
        history_details = []
        for reg in all_registers:
             ctx = {
                'reason_code': reg.reason.code,
                'month': reg.monthly_context.month_reference,
                'day_of_week': reg.week_day,
                'season': reg.season,
                'transport_expense': reg.transportation_expense,
                'work_load': reg.monthly_context.work_load_average,
                'hit_target': reg.monthly_context.hit_target,
                'disciplinary_failure': reg.disciplinary_failure,
            }
             history_details.append({
                "collaborator": reg.collaborator.full_name,
                "actual": reg.absenteeism_time,
                "predicted": round(predictor.predict_collaborator(reg.collaborator, ctx), 2),
                "date": f"{reg.monthly_context.month_reference}/{reg.monthly_context.year_reference}"
            })

        return {
            "current_month": {
                "actual_total": round(actual_current_total, 2),
                "predicted_total": round(predicted_current_total, 2),
                "gap": round(actual_current_total - predicted_current_total, 2)
            },
            "next_month": {
                "month_reference": next_month,
                "year_reference": next_year,
                "total_estimated_hour": round(next_month_forecast, 2),
                "details": projection_details
            },
            "history": {
                "details": history_details
            }
        }

    def get(self, request):
        data = self.get_dashboard_data(request.user)
        return Response(data)

    def post(self, request):
        data = self.get_dashboard_data(request.user, custom_context=request.data)
        return Response(data)

class BulkPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Bulk Prediction from File",
        description="Processes a CSV or Excel file and returns predictions for each row.",
        responses={200: {"type": "object"}}
    )
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "Nenhum arquivo enviado."}, status=400)

        start_time = time.time()

        try:
            if file_obj.name.endswith('.csv'):
                # Tenta ler com ; primeiro, se falhar ou encontrar 1 só coluna, tenta vírgula
                df = pd.read_csv(file_obj, sep=';', decimal=',')
                if len(df.columns) < 2:
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj, sep=',', decimal='.')
            elif file_obj.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_obj)
            else:
                return Response({"error": "Formato de arquivo não suportado. Use CSV ou Excel."}, status=400)

            # Limpar nomes das colunas (remover espaços extras no início/fim)
            df.columns = df.columns.str.strip()

            predictor = AbsenteeismPredictor()
            
            # Preparar matriz de features (vetorizado)
            features_matrix = []
            colab_names = []

            for index, row in df.iterrows():
                colab_names.append(row.get('Collaborator Name') or row.get('Name') or f"Colaborador {index+1}")
                
                features_matrix.append([
                    row.get('Reason for absence', 0),
                    row.get('Month of absence', 1),
                    row.get('Day of the week', 2),
                    row.get('Seasons', 1),
                    row.get('Transportation expense', 100.0),
                    row.get('Distance from Residence to Work', 20.0),
                    row.get('Service time', 5.0),
                    row.get('Age', 30.0),
                    row.get('Work load Average/day', 250.0),
                    row.get('Hit target', 90.0),
                    1 if row.get('Disciplinary failure') in [1, True, '1', 'True', 'true'] else 0,
                    row.get('Son', 0),
                    1 if row.get('Social drinker') in [1, True, '1', 'True', 'true'] else 0,
                    1 if row.get('Social smoker') in [1, True, '1', 'True', 'true'] else 0,
                    row.get('Pet', 0),
                    row.get('Body mass index', 25.0),
                ])
            
            # Predição em lote (MUITO mais rápido que um por um)
            all_predictions = predictor.predict_bulk(features_matrix)
            
            results = [
                {"collaborator": name, "predicted_hours": pred}
                for name, pred in zip(colab_names, all_predictions)
            ]

            end_time = time.time()
            processing_time = round(end_time - start_time, 3)

            if not results:
                return Response({"error": "Não foi possível processar nenhuma linha do arquivo."}, status=400)

            total_rows = len(results)
            avg_absenteeism = round(sum(r['predicted_hours'] for r in results) / total_rows, 2)
            ranking = sorted(results, key=lambda x: x['predicted_hours'])[:10]

            return Response({
                "summary": {
                    "total_rows": total_rows,
                    "average_predicted_hours": avg_absenteeism,
                    "processing_time_seconds": processing_time
                },
                "ranking": ranking
            })

        except Exception as e:
            return Response({"error": f"Erro ao processar arquivo: {str(e)}"}, status=500)

class CollaboratorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        collaborators = Collaborator.objects.filter(manager=request.user)
        data = [
            {"id": colab.id, "name": colab.full_name}
            for colab in collaborators
        ]
        return Response(data)

class ReasonListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reasons = ReasonAbsenteeism.objects.all().order_by('code')
        data = [
            {"code": r.code, "description": r.description}
            for r in reasons
        ]
        return Response(data)

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
