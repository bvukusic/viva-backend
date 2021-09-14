from datetime import date, datetime, timedelta
from django.shortcuts import render
from rest_framework import serializers, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

import users.models
import users.serializers
import appointments.models
import appointments.serializers

# Create your views here.
class AppointmentViewSet(APIView):
    def get(self, request, appointment_id, *args, **kwargs):
        queryset = appointments.models.Appointment.objects.get(id=appointment_id)
        serializer = appointments.serializers.AppointmentSerializer(queryset).data

        return Response({'appointment': serializer},
                        status=status.HTTP_200_OK)


class ListDoctorAppointments(APIView):
    def get(self, request, *args, **kwargs):
        queryset = appointments.models.Appointment.objects.filter(doctor=request.user.id).order_by('appointment_date')

        serializer = appointments.serializers.AppointmentSerializer(queryset, many=True).data

        return Response({'appointments': serializer},
                        status=status.HTTP_200_OK)

class PatientAppointmentView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    def get(self, request, *args, **kwargs):
        try:
            queryset = appointments.models.Appointment.objects.get(patient=request.user.id, appointment_date__gte=datetime.now().date())

            serializer = appointments.serializers.AppointmentSerializer(queryset).data
        except appointments.models.Appointment.DoesNotExist:
            return Response({'appointment': "No appointment"},
                        status=status.HTTP_200_OK)
        return Response({'appointment': serializer},
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        queryset = appointments.models.Appointment.objects.filter(doctor=request.data["doctor_id"], 
                                                            appointment_date__gte=datetime.now().date()).last()
        if not queryset:
            now = datetime.now()
            new_appointment = appointments.models.Appointment.objects.create_appointment(patient=users.models.User.objects.get(id=request.user.id), 
                                                            doctor=users.models.User.objects.get(id=request.data["doctor_id"]), 
                                                            appointment_date=datetime(now.year, now.month, now.day+1, 8))
            return Response(new_appointment, status=status.HTTP_201_CREATED)

        else:
            latest_appointment= appointments.serializers.AppointmentSerializer(queryset).data
            new_appointment = latest_appointment
            #increment hours up until 17:00, then add day
            new_date = datetime.strptime(latest_appointment["appointment_date"], "%Y-%m-%d").date()
            new_appointment["patient"] = request.user.id
            new_appointment["appointment_date"] = new_date + timedelta(minutes=30)
            new_appointment = appointments.models.Appointment.objects.create_appointment(patient=users.models.User.objects.get(id=new_appointment["patient"]), 
                                                            doctor=users.models.User.objects.get(id=request.data["doctor_id"]), 
                                                            appointment_date=new_appointment["appointment_date"])
            return Response(new_appointment, status=status.HTTP_201_CREATED)

class PatientNoteView(generics.CreateAPIView):

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = appointments.serializers.AppointmentNoteSerializer(data=data,
                                                        context={'user': self.request.user})
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

