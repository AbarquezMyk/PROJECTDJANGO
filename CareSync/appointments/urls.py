from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('choose-your-doctor/', views.choose_your_doctor, name='choose_your_doctor'),
    path('appointment_form/<str:doctor_name>/', views.appointment_form, name='appointment_form'),
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('appointment-history/', views.appointment_history, name='appointment_history'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('credit_card/', views.credit_card, name='credit_card'),
    path('cards/edit/<int:card_id>/', views.edit_card, name='edit_card'),
    path('cards/delete/<int:card_id>/', views.delete_card, name='delete_card'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.get_events, name='get_events'),
    path('calendar/events/add/', views.add_event, name='add_event'),
    path('calendar/events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('calendar/events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
]