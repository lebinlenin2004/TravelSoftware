from django.contrib import admin
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'base_price', 'seasonal_price', 
                    'tax_percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'destination', 'created_at']
    search_fields = ['name', 'destination', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'destination', 'duration_days')
        }),
        ('Pricing', {
            'fields': ('base_price', 'seasonal_price', 'tax_percentage', 
                      'commission_percentage', 'max_discount_percentage')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

