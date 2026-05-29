from django.urls import path
from .views import ModelMetricsView

urlpatterns = [
    path('model-metrics/', ModelMetricsView.as_view(), name='model-metrics'),
]
