from django.contrib import admin

# Register your models here.
from .models import Appointment
from appointments import models

@admin.register(models.Appointment)
class Appointment(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'appointment_date']

@admin.register(models.AppointmentNote)
class AppointmentNote(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'note', 'author']