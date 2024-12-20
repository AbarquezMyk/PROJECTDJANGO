from django.db import models
from django.conf import settings
from django.shortcuts import render
from admin_dashboard.models import Department, Doctor as AdminDashboardDoctor
from django.contrib.auth.models import User


class CreditCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cardholder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    cvc = models.CharField(max_length=4)

    @property
    def masked_card_number(self):
        return '**** **** **** ' + self.card_number[-4:]
    
def choose_your_doctor(request):
    departments = Department.objects.all()
    return render(request, 'appointments/choose_your_doctor.html', {'departments': departments})

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='doctors', blank=True, null=True)

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('upcoming', 'Upcoming'),
        ('past', 'Past'),
    ]

    id = models.AutoField(primary_key=True)
    # Reference to Doctor model from the 'admin_dashboard' app
    doctor = models.ForeignKey(
        'admin_dashboard.Doctor',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('none', 'None'),
            ('cash', 'Cash'),
            ('credit_card', 'Credit Card'),
        ],
        default='none',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["appointment_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["doctor", "patient"]),
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.appointment_date} [{self.status}]"


class Payment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255)

class Event(models.Model):
    title = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title