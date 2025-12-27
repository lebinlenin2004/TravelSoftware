from django.contrib import admin
from .models import Booking, AuditLog


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'customer_name', 'package', 'total_amount', 
                    'status', 'created_at', 'created_by']
    list_filter = ['status', 'travel_date', 'created_at', 'price_mismatch_flag', 
                   'excess_discount_flag', 'duplicate_booking_flag']
    search_fields = ['booking_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['booking_number', 'created_at', 'updated_at', 'validated_at',
                       'price_mismatch_flag', 'excess_discount_flag', 'duplicate_booking_flag']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_number', 'package', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Travel Details', {
            'fields': ('travel_date', 'number_of_travelers')
        }),
        ('Pricing', {
            'fields': ('package_price', 'discount_percentage', 'discount_amount',
                      'subtotal', 'tax_amount', 'total_amount', 'commission_amount')
        }),
        ('Validation', {
            'fields': ('validated_by', 'validated_at', 'validation_notes')
        }),
        ('Flags', {
            'fields': ('price_mismatch_flag', 'excess_discount_flag', 'duplicate_booking_flag'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'object_id', 'action', 'user', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['model_name', 'notes']
    readonly_fields = ['model_name', 'object_id', 'action', 'user', 'changes', 
                      'ip_address', 'timestamp', 'notes']
    date_hierarchy = 'timestamp'

