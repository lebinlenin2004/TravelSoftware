from django import forms
from django.core.validators import RegexValidator
from .models import Booking
from packages.models import Package
from decimal import Decimal
import re


class BookingForm(forms.ModelForm):
    """Form for creating/editing bookings."""
    
    package = forms.ModelChoiceField(
        queryset=Package.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_package'}),
        empty_label="Select a package"
    )
    
    class Meta:
        model = Booking
        fields = [
            'package', 'customer_name', 'customer_email', 'customer_phone',
            'customer_address', 'travel_date', 'number_of_travelers',
            'package_price', 'discount_percentage'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': 2,
                'maxlength': 200
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True,
                'type': 'email'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'minlength': '10',
                'placeholder': 'Enter 10 digit phone number'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'maxlength': 500
            }),
            'travel_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'required': True,
                'min': 'today'
            }),
            'number_of_travelers': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1,
                'max': 50,
                'required': True,
                'id': 'id_number_of_travelers'
            }),
            'package_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'readonly': True,
                'id': 'id_package_price'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0,
                'max': 100,
                'id': 'id_discount_percentage'
            }),
        }
    
    def clean_discount_percentage(self):
        """Validate discount percentage."""
        discount = self.cleaned_data.get('discount_percentage')
        package = self.cleaned_data.get('package')
        
        if package and discount:
            if discount > package.max_discount_percentage:
                raise forms.ValidationError(
                    f'Discount cannot exceed {package.max_discount_percentage}% for this package.'
                )
        
        return discount
    
    def clean_customer_name(self):
        """Validate customer name."""
        name = self.cleaned_data.get('customer_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Customer name must be at least 2 characters long.')
            if not re.match(r'^[a-zA-Z\s]+$', name):
                raise forms.ValidationError('Customer name can only contain letters and spaces.')
        return name
    
    def clean_customer_phone(self):
        """Validate phone number - must be exactly 10 digits."""
        phone = self.cleaned_data.get('customer_phone')
        if phone:
            # Remove any spaces, dashes, or other characters
            phone = re.sub(r'[^\d]', '', str(phone))
            if len(phone) != 10:
                raise forms.ValidationError('Phone number must be exactly 10 digits.')
            if not phone.isdigit():
                raise forms.ValidationError('Phone number must contain only digits.')
        return phone
    
    def clean_customer_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('customer_email')
        if email:
            email = email.strip().lower()
            # Basic email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise forms.ValidationError('Please enter a valid email address.')
        return email
    
    def clean_travel_date(self):
        """Validate travel date is not in the past."""
        travel_date = self.cleaned_data.get('travel_date')
        if travel_date:
            from django.utils import timezone
            today = timezone.now().date()
            if travel_date < today:
                raise forms.ValidationError('Travel date cannot be in the past.')
        return travel_date
    
    def clean_number_of_travelers(self):
        """Validate number of travelers."""
        travelers = self.cleaned_data.get('number_of_travelers')
        if travelers:
            if travelers < 1:
                raise forms.ValidationError('Number of travelers must be at least 1.')
            if travelers > 50:
                raise forms.ValidationError('Number of travelers cannot exceed 50.')
        return travelers
    
    def clean_package_price(self):
        """Validate package price matches current package price."""
        package_price = self.cleaned_data.get('package_price')
        package = self.cleaned_data.get('package')
        number_of_travelers = self.cleaned_data.get('number_of_travelers', 1)
        
        if package:
            expected_price = package.get_current_price() * number_of_travelers
            if abs(package_price - expected_price) > Decimal('0.01'):
                raise forms.ValidationError(
                    f'Price mismatch. Expected {expected_price} for {number_of_travelers} traveler(s).'
                )
        
        return package_price


class BookingValidationForm(forms.Form):
    """Form for validating bookings."""
    
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    validation_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter reason for approval/rejection...'
        }),
        help_text="Required for rejection, optional for approval"
    )
    
    def clean(self):
        """Validate that notes are provided for rejection."""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        notes = cleaned_data.get('validation_notes')
        
        if action == 'reject' and not notes:
            raise forms.ValidationError({
                'validation_notes': 'Validation notes are required when rejecting a booking.'
            })
        
        return cleaned_data

