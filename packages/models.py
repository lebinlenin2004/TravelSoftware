from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Package(models.Model):
    """Tour package model."""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    destination = models.CharField(max_length=200)
    duration_days = models.PositiveIntegerField(default=1)
    
    # Pricing
    base_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    seasonal_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Optional seasonal pricing"
    )
    
    # Tax and Commission
    tax_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('18.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="GST percentage"
    )
    commission_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    
    # Discount limits
    max_discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('20.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Maximum discount allowed (%)"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_packages'
    )
    
    class Meta:
        db_table = 'packages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.destination}"
    
    def get_current_price(self):
        """Get current price (seasonal if available, else base)."""
        return self.seasonal_price if self.seasonal_price else self.base_price
    
    def calculate_tax(self, amount):
        """Calculate tax amount."""
        return round(amount * (self.tax_percentage / Decimal('100')), 2)
    
    def calculate_commission(self, amount):
        """Calculate commission amount."""
        return round(amount * (self.commission_percentage / Decimal('100')), 2)

