from django.contrib import admin
from .models import Payment, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'payment_status', 'amount_paid', 'total_amount', 
                    'payment_method', 'payment_date', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'payment_date', 'created_at']
    search_fields = ['booking__booking_number', 'transaction_id', 'booking__customer_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'invoice_date', 'due_date']
    list_filter = ['invoice_date']
    search_fields = ['invoice_number', 'booking__booking_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'invoice_date'

