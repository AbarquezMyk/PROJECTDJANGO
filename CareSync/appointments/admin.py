from django.contrib import admin
from .models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty']

admin.site.register(Doctor, DoctorAdmin)