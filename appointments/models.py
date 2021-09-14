from datetime import date
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from users.models import User

# Create your models here.

class AppointmentManager(models.Manager):
    def create_appointment(self, patient, doctor, appointment_date):
        appointment = self.create(patient=patient, doctor=doctor, appointment_date=appointment_date)

        return appointment
        
class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='appointment_patient',
                             related_query_name='appointment_patient')
    doctor = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='appointment_doctor',
                             related_query_name='appointment_doctor')
    appointment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AppointmentManager()

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        db_table = 'appointment'

class AppointmentNoteManager(models.Manager):
    def create_appointment_note(self, note, appointment, author):
        appointment_note = self.create(note=note, appointment=appointment, author=author)

        return appointment_note

class AppointmentNote(models.Model):
    PATIENT = 'patient'
    DOCTOR = 'doctor'

    AUTHOR_CHOICE = (
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
    )

    id = models.AutoField(primary_key=True)
    note = models.CharField(max_length=300)
    appointment = models.ForeignKey(Appointment,
                             on_delete=models.CASCADE,
                             related_name='appointment_note',
                             related_query_name='appointment_note')
    author = models.CharField(max_length=30, choices=AUTHOR_CHOICE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AppointmentManager()

    class Meta:
        verbose_name = 'AppointmentNote'
        verbose_name_plural = 'Appointment Notes'
        db_table = 'appointment_note'

