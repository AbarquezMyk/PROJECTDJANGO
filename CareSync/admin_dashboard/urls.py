from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('departments/', views.add_department, name='departments'),
    path('doctors/', views.add_doctor, name='doctors'),
]