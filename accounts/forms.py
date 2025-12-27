from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from .models import User
import re


class LoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """User registration form (for admin use)."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]{10}',
            'maxlength': '10',
            'minlength': '10',
            'placeholder': 'Enter 10 digit phone number'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 
                  'phone', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean_phone(self):
        """Validate phone number - must be exactly 10 digits if provided."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces, dashes, or other characters
            phone = re.sub(r'[^\d]', '', str(phone))
            if len(phone) != 10:
                raise forms.ValidationError('Phone number must be exactly 10 digits.')
            if not phone.isdigit():
                raise forms.ValidationError('Phone number must contain only digits.')
        return phone
    
    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise forms.ValidationError('Please enter a valid email address.')
        return email

