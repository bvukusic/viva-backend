from datetime import date
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, commit=True):
        """
        Creates and saves a User with the given email, first name, last name
        and password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, first name,
        last name and password.
        """
        user = self.create_user(
            email,
            password=password,
            commit=False,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    MALE = 'male'
    FEMALE = 'female'
    PATIENT = 'patient'
    DOCTOR = 'doctor'

    GENDER_CHOICE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    ROLE_CHOICE = (
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
    )

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICE, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICE, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    activation_code = models.CharField(max_length=255, blank=True, null=True)
    
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return '{}'.format(self.email)

    def calculate_years_from_age(self):
        if self.dob is not None:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

        return None

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'

class PatientDoctor(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='+',
                             related_query_name='+')
    doctor = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='+',
                             related_query_name='+')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Doctor'
        verbose_name_plural = 'Patients Doctors'
        db_table = 'patient_doctor'



class UserTimelineEntry(models.Model):
    TERRIBLE = 'terrible'
    BAD = 'bad'
    NEUTRAL = 'neutral'
    GOOD = 'good'
    GREAT = 'great'

    MOOD_CHOICE = (
        (TERRIBLE, 'Terrible'),
        (BAD, 'Bad'),
        (NEUTRAL, 'Neutral'),
        (GOOD, 'Good'),
        (GREAT, 'Great'),
    )

    id = models.AutoField(primary_key=True)
    mood = models.CharField(max_length=30, choices=MOOD_CHOICE, blank=True, null=True)
    patient_note = models.CharField(max_length=100)
    entry_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='timeline_entries',
                             related_query_name='timeline_entries')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Timeline Entry'
        verbose_name_plural = 'User Timeline Entries'
        db_table = 'user_timeline_entry'

