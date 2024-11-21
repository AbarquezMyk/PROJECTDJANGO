from django.contrib import admin
from .models import Department, Doctor

class DepartmentAdmin(admin.ModelAdmin):
    pass

class DoctorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Doctor, DoctorAdmin)