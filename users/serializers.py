from rest_framework import serializers
from .models import User, UserTimelineEntry
from .models import PatientDoctor

class UserSerializer(serializers.ModelSerializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True, required=True)

        class Meta:
                model = User
                fields = ('id', 'email', 'password', 'dob', 'gender', 'role', 'first_name', 'last_name')
        def create(self, validated_data):
                user = super(UserSerializer, self).create(validated_data)
                user.set_password(validated_data['password'])
                user.save()
                return user

class PatientDoctorListSerializer(serializers.ModelSerializer):
        patient = serializers.SerializerMethodField()

        class Meta:
                model = PatientDoctor
                fields = ['id', 'patient']

        def get_patient(self, obj):
                patients = User.objects.get(id = obj.patient.id)

                return UserSerializer(patients).data

class PatientHasDoctorSerializer(serializers.ModelSerializer):
        doctor = serializers.SerializerMethodField()

        class Meta:
                model = PatientDoctor
                fields = ['doctor']

        def get_doctor(self, obj):
                doctor = User.objects.get(id = obj.doctor.id)

                return UserSerializer(doctor).data

class UserTimelineEntrySerializer(serializers.ModelSerializer):

        class Meta:
                model = UserTimelineEntry
                fields = ['id', 'mood', 'entry_date', 'patient_note', 'user_id']
        def create(self, validated_data):
                validated_data["user"]=self.context["user"]
                response = super(UserTimelineEntrySerializer, self).create(validated_data)

                # response.user = self.context['user']
                response.save()

                return response
        

