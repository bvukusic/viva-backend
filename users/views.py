import datetime
import logging

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt import views as jwt_views
from rest_framework import generics, status, viewsets, permissions, renderers
from rest_framework_simplejwt import views as jwt_views
from rest_framework.views import APIView
from rest_framework.response import Response
from firebase_admin.messaging import Message, Notification
from django.core.exceptions import ValidationError
from django.core import validators
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from users.models import PatientDoctor, User, UserTimelineEntry
import users.models
import users.serializers
import users.service

@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Users':'/users/',
        }
    
    return Response(api_urls)

class LoginView(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            if not self.request.data.get('email'):
                return Response({'status': 'error',
                                    'errors': {'email': ['Email is required']}},
                                status=status.HTTP_400_BAD_REQUEST)

            if not self.request.data.get('password'):
                return Response({'status': 'error',
                                    'errors': {'password': ['Password is required']}},
                                status=status.HTTP_400_BAD_REQUEST)

            response = super().post(request)
            user = users.serializers.UserSerializer(
                users.models.User.objects.get(email=request.data.get("email"))).data

        except (users.models.User.DoesNotExist, ValidationError) as e:
            logging.error(e)
            return Response({'status': 'error',
                                'errors': {'email': 'No account with given credentials.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'success',
                            'user': user,
                            'token': response.data},
                        status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = users.models.User.objects.all()
    serializer_class = users.serializers.UserSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.AllowAny(),

        if self.request.method == 'POST':
            return permissions.AllowAny(),

        return permissions.IsAuthenticated(),

    def retrieve(self, request, *args, **kwargs):
        """
        Returns data on a particular user.

        returns:
          - application/json
        """
        queryset = users.models.User.objects.all()
        user = get_object_or_404(queryset, id=request.user.id)
        serializer = users.serializers.UserSerializer(user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new user.

        returns:
          - application/json
        """
        confirm_password = request.data.pop('confirm_password', None)

        if confirm_password == request.data.get('password'):
            try:
                new_user = users.serializers.UserSerializer(data=request.data)

                if new_user.is_valid():
                    new_user.save()
                else:
                    logging.error(new_user.errors)
                    return Response({
                        'status': 'error',
                        'errors': new_user.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as e:
                return Response({'status': 'error', 'errors': {'error': e.args}}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'success',
                             'user': new_user.data,
                             'token': users.service.get_tokens_for_user(new_user.instance)},
                            status=status.HTTP_201_CREATED)

        return Response({'status': 'error',
                         'errors': {'password': ['Passwords do not match!']}},
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update the information of a user.

        returns:
          - application/json
        """
        try:
            user = users.models.User.objects.get(id=request.user.id)
            serializer = users.serializers.UserSerializer(user, data=request.data, partial=True)

            if self.request.data.get('dob', None):
                today = datetime.datetime.today()
                dob = datetime.datetime.strptime(self.request.data.get('dob'), '%Y-%m-%d')
                if today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)) < 18:
                    return Response({'status': 'error', 'errors': {'dob': 'You must be 18 years of age to use Mydelica'}},
                                    status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                user = serializer.save()
                return Response({"user": users.serializers.UserSerializer(user).data,
                                 "token": users.service.get_tokens_for_user(user)},
                                status=status.HTTP_200_OK)
            else:
                logging.error(serializer.errors)
                return Response({
                    'status': 'Bad request',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            if 'email' in str(e.args):
                return Response({'status': 'error', 'errors': {'email': 'User with this e-mail already exists.'}},
                                status=status.HTTP_400_BAD_REQUEST)
            elif 'username' in str(e.args):
                return Response({'status': 'error', 'errors': {'username': 'User with this username already exists.'}},
                                status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def userList(request):
    users_list = users.models.User.objects.all()
    serializer = users.serializers.UserSerializer(users_list, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def doctorList(request):
    doctors = User.objects.filter(role = 'doctor')
    serializer = users.serializers.UserSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def doctorPatientList(request):
    queryset = PatientDoctor.objects.filter(doctor = request.user.id)
    serializer = users.serializers.PatientDoctorListSerializer(queryset, many=True).data

    return Response({'patients': serializer},
                    status=status.HTTP_200_OK)

class PatientHasDoctorView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    
    def get(self, request, *args, **kwargs):
        try:
            queryset = PatientDoctor.objects.get(patient = request.user.id)
            serializer = users.serializers.PatientHasDoctorSerializer(queryset).data
            return Response({"data": serializer, "message": "Has doctor assigned"})
        except PatientDoctor.DoesNotExist:
            return Response({"message": "No doctor assigned"})
           

    def create(self, request, *args, **kwargs):
        patient_doctor, created = PatientDoctor.objects.get_or_create(patient=User.objects.get(id=request.user.id),
                                    defaults={'doctor': User.objects.get(id=request.data.get('doctor'))})
        serializer = users.serializers.PatientHasDoctorSerializer(patient_doctor).data

        return Response({"data": serializer, "created": created}, status=status.HTTP_200_OK)

class UserTimelineEntriesView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = users.serializers.UserTimelineEntrySerializer
    queryset = users.models.UserTimelineEntry.objects.all().order_by('created_at')
    lookup_id = 'id'
    
    def get(self, request):
        queryset = UserTimelineEntry.objects.filter(user=request.user.id)

        serializer = users.serializers.UserTimelineEntrySerializer(queryset, many=True).data

        return Response(serializer)

           

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = users.serializers.UserTimelineEntrySerializer(data=data,
                                                        context={'user': self.request.user})
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PatientTimelineEntriesView(APIView):
    def get(self, request, patient_id, *args, **kwargs):
        queryset = UserTimelineEntry.objects.filter(user=patient_id)
        serializer = users.serializers.UserTimelineEntrySerializer(queryset, many=True).data

        return Response(serializer)