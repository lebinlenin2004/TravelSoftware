from django import forms
from decimal import Decimal
from .models import Package


class PackageForm(forms.ModelForm):
    """Form for creating/editing packages."""
    
    class Meta:
        model = Package
        fields = [
            'name', 'description', 'destination', 'duration_days',
            'base_price', 'seasonal_price', 'tax_percentage',
            'commission_percentage', 'max_discount_percentage', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': 3,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'maxlength': 1000
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': 2,
                'maxlength': 200
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1,
                'max': 365,
                'required': True
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0.01,
                'required': True
            }),
            'seasonal_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0.01
            }),
            'tax_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0,
                'max': 100,
                'required': True
            }),
            'commission_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0,
                'max': 100,
                'required': True
            }),
            'max_discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0,
                'max': 100,
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        """Validate package name."""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 3:
                raise forms.ValidationError('Package name must be at least 3 characters long.')
        return name
    
    def clean_base_price(self):
        """Validate base price."""
        price = self.cleaned_data.get('base_price')
        if price and price <= 0:
            raise forms.ValidationError('Base price must be greater than 0.')
        return price
    
    def clean_seasonal_price(self):
        """Validate seasonal price."""
        price = self.cleaned_data.get('seasonal_price')
        if price and price <= 0:
            raise forms.ValidationError('Seasonal price must be greater than 0.')
        return price
    
    def clean_tax_percentage(self):
        """Validate tax percentage."""
        tax = self.cleaned_data.get('tax_percentage')
        if tax:
            if tax < 0 or tax > 100:
                raise forms.ValidationError('Tax percentage must be between 0 and 100.')
        return tax
    
    def clean_commission_percentage(self):
        """Validate commission percentage."""
        commission = self.cleaned_data.get('commission_percentage')
        if commission:
            if commission < 0 or commission > 100:
                raise forms.ValidationError('Commission percentage must be between 0 and 100.')
        return commission
    
    def clean_max_discount_percentage(self):
        """Validate max discount percentage."""
        discount = self.cleaned_data.get('max_discount_percentage')
        if discount:
            if discount < 0 or discount > 100:
                raise forms.ValidationError('Max discount percentage must be between 0 and 100.')
        return discount
    
    def clean_duration_days(self):
        """Validate duration days."""
        days = self.cleaned_data.get('duration_days')
        if days:
            if days < 1:
                raise forms.ValidationError('Duration must be at least 1 day.')
            if days > 365:
                raise forms.ValidationError('Duration cannot exceed 365 days.')
        return days

