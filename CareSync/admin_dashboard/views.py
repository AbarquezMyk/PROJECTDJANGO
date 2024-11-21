from django.shortcuts import render, redirect
from .forms import DepartmentForm, DoctorForm
from .models import Department, Doctor
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('admin_dashboard.view_dashboard')
def admin_dashboard(request):
    return render(request, 'admin_dashboard/dashboard.html')

@permission_required('admin_dashboard.add_department')
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:departments')
    else:
        form = DepartmentForm()
    return render(request, 'admin_dashboard/add_department.html', {'form': form})

@permission_required('admin_dashboard.add_doctor')
def add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:doctors')
    else:
        form = DoctorForm()
    return render(request, 'admin_dashboard/add_doctor.html', {'form': form})