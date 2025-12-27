from django.db import models
from decimal import Decimal


class Payment(models.Model):
    """Payment model for bookings."""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments'
    )
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for {self.booking.booking_number} - {self.payment_status}"
    
    def get_balance(self):
        """Calculate remaining balance."""
        return self.total_amount - self.amount_paid
    
    def update_status(self):
        """Update payment status based on amount paid."""
        if self.amount_paid >= self.total_amount:
            self.payment_status = 'paid'
        elif self.amount_paid > Decimal('0.00'):
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        self.save()


class Invoice(models.Model):
    """Invoice model."""
    
    invoice_number = models.CharField(max_length=50, unique=True)
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"

