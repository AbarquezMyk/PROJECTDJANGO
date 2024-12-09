from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm, ProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from django.utils.timezone import now

def dashboard_view(request):
    # Fetch upcoming appointments for the logged-in user
    upcoming_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date__gte=now()
    ).order_by('appointment_date')
    
    context = {
        'first_name': request.user.first_name,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    if request.user.is_authenticated:
        return render(request, 'patients/register.html', {'form': form, 'first_name': request.user.first_name, 'last_name': request.user.last_name})
    else:
        return render(request, 'patients/register.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
    else:
        form = LoginForm()
    return render(request, 'patients/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'patients/home.html')

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'patients/dashboard.html', {'first_name': request.user.first_name, 'last_name': request.user.last_name})
    else:
        return redirect('login')
    
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'patients/profile.html', {'form': form})