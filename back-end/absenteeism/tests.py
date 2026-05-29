from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
import os
from django.conf import settings

class ModelMetricsTests(APITestCase):
    def test_model_metrics_success(self):
        url = reverse('model-metrics')
        data = {'percentage': 10}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', response.data)
        self.assertIn('mae', response.data['metrics'])
        self.assertIn('rmse', response.data['metrics'])
        self.assertIn('r2_score', response.data['metrics'])
        self.assertIn('scatter_plot_data', response.data)
        self.assertTrue(len(response.data['scatter_plot_data']) > 0)

    def test_model_metrics_invalid_percentage(self):
        url = reverse('model-metrics')
        data = {'percentage': 101}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_model_metrics_missing_percentage(self):
        url = reverse('model-metrics')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
