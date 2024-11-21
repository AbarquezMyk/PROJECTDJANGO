from django import forms
from .models import Doctor
from .models import CreditCard

class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['cardholder_name', 'card_number', 'expiration_date', 'cvc']
        widgets = {
            'cardholder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cardholder Name'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}),
            'expiration_date': forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}, format='%Y-%m'),
            'cvc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVC'}),
        }

    # Ensure the form accepts 'yyyy-mm' format for expiration_date
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expiration_date'].input_formats = ['%Y-%m']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'specialty', 'department', 'picture')