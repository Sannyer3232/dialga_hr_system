from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
import pandas as pd
import joblib
import numpy as np
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from django.conf import settings

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
        model_path = os.path.join(base_path, 'Dialgah_Prev.pkl')
        scaler_path = os.path.join(base_path, 'Dialgah_Scaler.pkl')
        data_path = os.path.join(base_path, 'data', 'Dialgah_Dados_Teste_DEMO.csv')

        try:
            # Load model and scaler
            model = joblib.load(model_path)
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
            
            # Reshape for model if needed (based on the error, it expects (None, 1, 16))
            # If the model is a TensorFlow model, it might need this reshape
            try:
                if hasattr(model, 'layers'): # Check if it's a Keras/TensorFlow model
                     X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
            except:
                pass

            # Predict
            y_pred = model.predict(X_scaled)
            
            # If model returns a 2D array (e.g. from Keras or some scikit-learn models), flatten it
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
