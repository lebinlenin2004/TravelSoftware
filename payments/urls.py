from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payments/', views.payment_list, name='list'),
    path('payments/<int:pk>/', views.payment_detail, name='detail'),
    path('bookings/<int:booking_id>/payment/create/', views.payment_create, name='create'),
    path('payments/<int:pk>/update/', views.payment_update, name='update'),
    path('bookings/<int:booking_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('invoices/<int:pk>/', views.view_invoice, name='view_invoice'),
]

