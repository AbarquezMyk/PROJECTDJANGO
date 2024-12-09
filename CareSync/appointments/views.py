from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment, Payment, Doctor
from admin_dashboard.models import Department
from admin_dashboard.models import Doctor as AdminDashboardDoctor
from django.contrib import messages
from .models import CreditCard
from .forms import CreditCardForm
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
from .models import Event
from django.utils.timezone import now  # Import `now`


def choose_your_doctor(request):
    departments = Department.objects.all()
    print(departments)
    return render(request, 'appointments/choose_your_doctor.html', {'departments': departments})

@login_required
def appointment_form(request, doctor_name):
    doctor = AdminDashboardDoctor.objects.get(name=doctor_name)
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        reason = request.POST.get('reason')
        print(f"Received data: {appointment_date}, {reason}, {request.user.username}")
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            reason=reason
        )
        print(f"Appointment created: {appointment}")
        return redirect('appointments:appointment_history')
    return render(request, 'appointments/appointment_form.html', {'doctor': doctor})


@login_required
def pay_appointment(request, appointment_id):
    # Fetch the appointment and ensure it's for the logged-in user
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    credit_cards = CreditCard.objects.filter(user=request.user)  # Define credit_cards
    payment_amount = 500  # Fixed payment amount

    # Ensure the appointment is still pending payment
    if appointment.status != 'pending':
        messages.error(request, "This appointment has already been paid or is no longer pending.")
        return redirect('appointments:appointment_history')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'cash':
            # Handle cash payment
            appointment.status = 'upcoming'
            appointment.payment_method = 'cash'
            appointment.save()
            messages.success(request, f"Payment of {payment_amount} was successful. Your appointment has been confirmed.")
            return redirect('appointments:appointment_history')
        
        elif payment_method == 'credit_card':
            credit_card_id = request.POST.get('credit_card_id')
            selected_card = get_object_or_404(CreditCard, id=credit_card_id, user=request.user)
            
            # Placeholder for payment gateway integration
            # e.g., process_payment(selected_card, payment_amount)
            
            appointment.status = 'upcoming'
            appointment.payment_method = f"Card ending in {selected_card.card_number[-4:]}"
            appointment.save()
            messages.success(request, f"Payment of {payment_amount} was successful. Your appointment has been confirmed.")
            return redirect('appointments:appointment_history')

    # Render the payment page with credit card options
    return render(request, 'appointments/pay.html', {
        'appointment': appointment,
        'credit_cards': credit_cards,
        'payment_amount': payment_amount,  # Pass payment amount to the template
    })


@login_required
def appointment_history(request):
    # Fetch and categorize appointments for the logged-in user
    pending_appointments = Appointment.objects.filter(
        patient=request.user, status='pending'
    ).order_by('appointment_date')
    
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user, status='upcoming', appointment_date__gte=now()
    ).order_by('appointment_date')
    
    past_appointments = Appointment.objects.filter(
        patient=request.user, appointment_date__lt=now()
    ).exclude(status='pending').order_by('-appointment_date')

    return render(request, 'appointments/appointment_history.html', {
        'pending_appointments': pending_appointments,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    })


@login_required
def payment_history(request):
    payments = Payment.objects.filter(appointment__patient=request.user)
    return render(request, 'appointments/payment_history.html', {'payments': payments})

@login_required
def credit_card(request):
    user = request.user
    cards = CreditCard.objects.filter(user=user)

    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.save()
            messages.success(request, "Card added successfully.")
            return redirect('appointments:credit_card')  # Redirect to the same page to display the updated list
        else:
            print(form.errors)
    else:
        form = CreditCardForm()

    context = {
        'cards': cards,
        'form': form,
        'card_to_edit': None,  # To differentiate when a new card is being added vs. edited
    }
    return render(request, 'appointments/credit_card.html', context)

@login_required
def edit_card(request, card_id):
    user = request.user
    card = get_object_or_404(CreditCard, id=card_id, user=user)
    cards = CreditCard.objects.filter(user=user)  # Fetch all cards for the current user

    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, "Card updated successfully.")
            return redirect('appointments:credit_card')
    else:
        form = CreditCardForm(instance=card)

    context = {
        'cards': cards,  # Pass the list of cards to show them while editing
        'form': form,
        'card_to_edit': card,  # This will trigger the template to know it's in edit mode
        'edit_mode': True,
    }
    return render(request, 'appointments/credit_card.html', context)

@login_required
def delete_card(request, card_id):
    card = get_object_or_404(CreditCard, id=card_id, user=request.user)

    if request.method == 'POST':
        card.delete()
        messages.success(request, "Card deleted successfully.")
        return redirect('appointments:credit_card')

    return render(request, 'appointments/credit_card.html', {'card': card})

@login_required
def calendar_view(request):
    """Render the calendar page."""
    return render(request, 'appointments/calendar.html')


def get_events(request):
    """Fetch all events for FullCalendar."""
    events = Event.objects.all().values('id', 'title', 'start', 'end')
    event_list = [
        {
            'id': event['id'],
            'title': event['title'],
            'start': event['start'].isoformat(),
            'end': event['end'].isoformat() if event['end'] else None,
        }
        for event in events
    ]
    return JsonResponse(event_list, safe=False)


@csrf_exempt
def add_event(request):
    """Add a new event to the calendar."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            start = data.get('start')

            if not title or not start:
                return JsonResponse({'error': 'Title and start time are required'}, status=400)

            start_dt = parse_datetime(start)
            if not start_dt:
                return JsonResponse({'error': 'Invalid start date format'}, status=400)

            event = Event.objects.create(title=title, start=start_dt)
            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start.isoformat()
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def edit_event(request, event_id):
    """Edit an existing event."""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            start = data.get('start')
            start_dt = parse_datetime(start)

            event = Event.objects.get(id=event_id)
            if title:
                event.title = title
            if start_dt:
                event.start = start_dt
            event.save()

            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start.isoformat()
            }, status=200)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_event(request, event_id):
    """Delete an event from the calendar."""
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'status': 'Event deleted'}, status=200)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_upcoming_appointments(request):
    if request.user.is_authenticated:
        appointments = Appointment.objects.filter(user=request.user, appointment_date__gte=now())
        appointment_data = [
            {
                "id": appt.id,
                "title": f"Appointment with {appt.doctor.name}",
                "start": appt.appointment_date.isoformat(),
                "description": appt.reason,
            }
            for appt in appointments
        ]
        return JsonResponse(appointment_data, safe=False)
    else:
        return JsonResponse({"error": "Unauthorized"}, status=401)

@login_required
def calendar_appointments(request):
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user, appointment_date__gte=now()
    ).order_by('appointment_date')

    data = [
        {
            "id": appt.id,
            "title": f"Appointment with Dr. {appt.doctor.name}",
            "start": appt.appointment_date.isoformat(),
            "description": appt.reason,
        }
        for appt in upcoming_appointments
    ]
    return JsonResponse(data, safe=False)