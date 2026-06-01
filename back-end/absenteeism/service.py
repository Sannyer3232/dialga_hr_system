import os
import joblib
import numpy as np
from tensorflow.keras.models import load_model
from django.conf import settings

class AbsenteeismPredictor:
    _instance = None
    _model = None
    _scaler = None

    def __new__(cls):
        """Implementação de Singleton para evitar de carregar o modelo em toda requisição."""
        if cls._instance is None:
            cls._instance = super(AbsenteeismPredictor, cls).__new__(cls)
            cls._load_assets()
        return cls._instance

    @classmethod
    def _load_assets(cls):
        base_path = os.path.join(settings.BASE_DIR, "machine_learning_models")
        model_path = os.path.join(base_path, 'Dialgah_LSTM_Mestre_3.keras')
        scaler_path = os.path.join(base_path,'Dialgah_Scaler.pkl')

        cls._model = load_model(model_path)
        cls._scaler = joblib.load(scaler_path)
    
    def predict(self, features_array):
        """
            Recebe o array/lista com as features, 
            aplica o scaler, faz o reshape e retorna a predição
        """

        X_scaled = self._scaler.transform([features_array])

        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

        prediction = self._model.predict(X_reshaped, verbose= 0)

        return round(float(prediction[0][0]), 2)

    def predict_collaborator(self, collaborator, context_data):
            """
            Método de conveniência que extrai dados do objeto Collaborator 
            e combina com o contexto (mês, dia da semana, etc.)
            """
            # Aqui você montaria a lista de 16 features baseada no seu CSV:
            # [Reason, Month, Day, Seasons, Distance, ServiceTime, Age, WorkLoad, Target, Failure, Son, Drinker, Smoker, Pet, BMI]
            # (A ordem exata deve seguir a do seu arquivo CSV de treino)
            
            features = [
                context_data.get('reason_code', 0),
                context_data.get('month', 1),
                context_data.get('day_of_week', 2),
                context_data.get('season', 1),
                context_data.get('transport_expense', 100.0),
                collaborator.work_distance,
                collaborator.service_years,
                collaborator.age,
                context_data.get('work_load', 200.0),
                context_data.get('hit_target', 90),
                1 if context_data.get('disciplinary_failure') else 0,
                collaborator.familiar_profile.first().sons if collaborator.familiar_profile.exists() else 0,
                1 if collaborator.health_profile.first().social_drinker else 0,
                1 if collaborator.health_profile.first().social_smoker else 0,
                collaborator.familiar_profile.first().pets if collaborator.familiar_profile.exists() else 0,
                collaborator.health_profile.first().bmi if collaborator.health_profile.exists() else 0,
            ]
            
            return self.predict(features)