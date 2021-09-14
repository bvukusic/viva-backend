from django.urls import path, include
import appointments.views

urlpatterns = [
    path('<int:appointment_id>/',
         appointments.views.AppointmentViewSet.as_view(),
         name='appointment-details'),
    path('doctor-appointments/',
         appointments.views.ListDoctorAppointments.as_view(),
         name='doctor-appointments'),
    path('patient-appointment/',
         appointments.views.PatientAppointmentView.as_view(),
         name='patient-appointment'),
    path('notes/',
         appointments.views.PatientNoteView.as_view(),
         name='notes'),
]
