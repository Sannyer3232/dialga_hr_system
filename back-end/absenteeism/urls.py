from django.urls import path
from .views import ModelMetricsView, ManagerDashboardView, CollaboratorSimulationView, CollaboratorListView, ReasonListView, BulkPredictionView

urlpatterns = [
    path('model-metrics/', ModelMetricsView.as_view(), name='model-metrics'),
    path('dashboard/', ManagerDashboardView.as_view(), name = 'manager-dasboard'),
    path('simulate/', CollaboratorSimulationView.as_view(), name = 'simulator'),
    path('collaborators/', CollaboratorListView.as_view(), name = 'collaborator-list'),
    path('reasons/', ReasonListView.as_view(), name = 'reason-list'),
    path('bulk-prediction/', BulkPredictionView.as_view(), name='bulk-prediction'),
]
