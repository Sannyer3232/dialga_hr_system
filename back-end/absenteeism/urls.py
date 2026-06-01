from django.urls import path
from .views import ModelMetricsView, ManagerDashboardView, CollaboratorSimulationView

urlpatterns = [
    path('model-metrics/', ModelMetricsView.as_view(), name='model-metrics'),
    path('dashboard/', ManagerDashboardView.as_view(), name = 'manager-dasboard'),
    path('simulate/', CollaboratorSimulationView.as_view(), name = 'simulator')
]
