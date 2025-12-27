from django import forms
from django.utils import timezone
from decimal import Decimal
from .models import Payment


class PaymentForm(forms.ModelForm):
    """Form for recording payments."""
    
    class Meta:
        model = Payment
        fields = [
            'payment_method', 'transaction_id', 'amount_paid', 'payment_date', 'notes'
        ]
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': 0,
                'required': True
            }),
            'payment_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set input format for datetime-local
        if self.instance and self.instance.payment_date:
            # Convert to local time for display
            local_time = timezone.localtime(self.instance.payment_date)
            self.fields['payment_date'].widget.attrs['value'] = local_time.strftime('%Y-%m-%dT%H:%M')
        elif not self.instance.pk:
            # Set default to current time for new payments
            self.fields['payment_date'].widget.attrs['value'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
    
    def clean_amount_paid(self):
        """Validate amount paid."""
        amount = self.cleaned_data.get('amount_paid')
        if amount is None:
            raise forms.ValidationError('Amount paid is required.')
        if amount < 0:
            raise forms.ValidationError('Amount paid cannot be negative.')
        return amount
    
    def clean(self):
        """Validate payment amount against total amount."""
        cleaned_data = super().clean()
        amount_paid = cleaned_data.get('amount_paid')
        
        if self.instance and self.instance.pk:
            # For updates, check against existing total_amount
            total_amount = self.instance.total_amount
            if amount_paid and amount_paid > total_amount:
                raise forms.ValidationError({
                    'amount_paid': f'Amount paid (₹{amount_paid}) cannot exceed total amount (₹{total_amount}).'
                })
        
        return cleaned_data

