from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/financial/', views.financial_report, name='financial_report'),
    path('reports/agents/', views.agent_performance, name='agent_performance'),
]

