from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('view_dashboard', 'Can view dashboard'),
        ]

class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='doctors', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.specialty})"