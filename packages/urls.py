from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('packages/', views.package_list, name='list'),
    path('packages/create/', views.package_create, name='create'),
    path('packages/<int:pk>/', views.package_detail, name='detail'),
    path('packages/<int:pk>/edit/', views.package_edit, name='edit'),
    path('api/package/<int:pk>/', views.package_api, name='api'),
]

