from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class Booking(models.Model):
    """Booking/Sales entry model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Validation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Booking Details
    booking_number = models.CharField(max_length=50, unique=True)
    package = models.ForeignKey('packages.Package', on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField(blank=True)
    
    # Travel Details
    travel_date = models.DateField()
    number_of_travelers = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Pricing
    package_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Commission
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Validation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    validation_notes = models.TextField(blank=True, help_text="Reason for approval/rejection")
    validated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_bookings'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    
    # Flags for suspicious activity
    price_mismatch_flag = models.BooleanField(default=False)
    excess_discount_flag = models.BooleanField(default=False)
    duplicate_booking_flag = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_bookings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['travel_date']),
        ]
    
    def __str__(self):
        return f"Booking #{self.booking_number} - {self.customer_name}"
    
    def calculate_totals(self):
        """Calculate all pricing totals."""
        # Calculate discount
        if self.discount_percentage > 0:
            self.discount_amount = round(
                self.package_price * (self.discount_percentage / Decimal('100')), 
                2
            )
        else:
            self.discount_amount = Decimal('0.00')
        
        # Calculate subtotal
        self.subtotal = round(self.package_price - self.discount_amount, 2)
        
        # Calculate tax
        self.tax_amount = round(
            self.subtotal * (self.package.tax_percentage / Decimal('100')), 
            2
        )
        
        # Calculate total
        self.total_amount = round(self.subtotal + self.tax_amount, 2)
        
        # Calculate commission
        self.commission_amount = round(
            self.subtotal * (self.package.commission_percentage / Decimal('100')), 
            2
        )
    
    def validate_pricing(self):
        """Validate pricing and set flags."""
        errors = []
        
        # Check price mismatch
        expected_price = self.package.get_current_price() * self.number_of_travelers
        if abs(self.package_price - expected_price) > Decimal('0.01'):
            self.price_mismatch_flag = True
            errors.append(f"Price mismatch: Expected {expected_price}, got {self.package_price}")
        else:
            self.price_mismatch_flag = False
        
        # Check excess discount
        if self.discount_percentage > self.package.max_discount_percentage:
            self.excess_discount_flag = True
            errors.append(
                f"Excess discount: {self.discount_percentage}% exceeds max {self.package.max_discount_percentage}%"
            )
        else:
            self.excess_discount_flag = False
        
        return errors
    
    def check_duplicate(self):
        """Check for duplicate bookings."""
        duplicates = Booking.objects.filter(
            customer_email=self.customer_email,
            package=self.package,
            travel_date=self.travel_date,
            status__in=['pending', 'approved']
        ).exclude(pk=self.pk)
        
        if duplicates.exists():
            self.duplicate_booking_flag = True
            return True
        else:
            self.duplicate_booking_flag = False
            return False
    
    def approve(self, user, notes=''):
        """Approve the booking."""
        self.status = 'approved'
        self.validated_by = user
        self.validated_at = timezone.now()
        if notes:
            self.validation_notes = notes
        self.save()
    
    def reject(self, user, notes):
        """Reject the booking."""
        self.status = 'rejected'
        self.validated_by = user
        self.validated_at = timezone.now()
        self.validation_notes = notes
        self.save()


class AuditLog(models.Model):
    """Audit log for tracking all changes."""
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
    ]
    
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} #{self.object_id} by {self.user}"

