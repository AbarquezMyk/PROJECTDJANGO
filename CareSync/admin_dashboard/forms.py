from django import forms
from .models import Department, Doctor

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'description')

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'specialty', 'department', 'picture')