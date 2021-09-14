from rest_framework import serializers
import appointments.models
from users.models import User
import users.serializers

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = appointments.models.Appointment
        fields = ('id', 'appointment_date', 'doctor', 'patient', 'notes')

    def get_doctor(self, obj):
        patients = User.objects.get(id = obj.doctor.id)
        return users.serializers.UserSerializer(patients).data

    def get_patient(self, obj):
        patients = User.objects.get(id = obj.patient.id)
        return users.serializers.UserSerializer(patients).data

    def get_notes(self, obj):
        appointment_notes = appointments.models.AppointmentNote.objects.filter(appointment_id=obj.id).all()

        return AppointmentNoteSerializer(appointment_notes, many=True).data

class AppointmentNoteSerializer(serializers.ModelSerializer):
    class Meta:
            model = appointments.models.AppointmentNote
            fields = ('id', 'note', 'author', 'appointment')
    
    def create(self, validated_data):
                response = super(AppointmentNoteSerializer, self).create(validated_data)

                response.save()

                return response

