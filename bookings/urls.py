from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('bookings/', views.booking_list, name='list'),
    path('bookings/create/', views.booking_create, name='create'),
    path('bookings/<int:pk>/', views.booking_detail, name='detail'),
    path('bookings/<int:pk>/validate/', views.booking_validate, name='validate'),
    path('bookings/pending/', views.pending_validations, name='pending'),
]

