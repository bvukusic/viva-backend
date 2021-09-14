from django.urls import path, include
import users.views

urlpatterns = [
    path('auth/login/', users.views.LoginView.as_view(), name='token_obtain_pair'),
    path('users/', users.views.UserViewSet.as_view({'post': 'create', 'get': 'retrieve', 'patch': 'update'}),
        name='users'),
    path('', users.views.apiOverview, name="api-overview"),
    path('user-list/', users.views.userList, name="user-list"),
    path('doctor-list/', users.views.doctorList, name="doctor-list"),
    path('doctor-patient-list/', users.views.doctorPatientList, name="doctor-patient-list"),
    path('patient-has-doctor/', users.views.PatientHasDoctorView.as_view(), name='patient-has-doctor'),
    path('user-timeline-entries/', users.views.UserTimelineEntriesView.as_view(), name='user-timeline-entries'),
    path('user-timeline-entries/<int:patient_id>/', users.views.PatientTimelineEntriesView.as_view(), name='patient-timeline-entries'),
]
