from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access control."""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('sales_agent', 'Sales Agent'),
        ('manager', 'Manager'),
        ('accountant', 'Accountant'),
        ('auditor', 'Auditor'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales_agent')
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_sales_agent(self):
        return self.role == 'sales_agent'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_accountant(self):
        return self.role == 'accountant'
    
    def is_auditor(self):
        return self.role == 'auditor'
    
    def can_create_booking(self):
        """Check if user can create bookings."""
        return self.is_admin() or self.is_sales_agent()
    
    def can_validate_booking(self):
        """Check if user can validate bookings."""
        return self.is_admin() or self.is_manager()
    
    def can_view_analytics(self):
        """Check if user can view analytics."""
        return self.is_admin() or self.is_manager() or self.is_accountant()
    
    def can_view_financial_reports(self):
        """Check if user can view financial reports."""
        return self.is_admin() or self.is_accountant()
    
    def has_read_access(self):
        """Check if user has read access (all roles)."""
        return True

