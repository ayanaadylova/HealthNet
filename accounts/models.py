from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
from django.core.validators import RegexValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('Staff Status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def get_message_count(self):
        count = 0
        for message in self.receiver.all():
            if not message.deleted:
                count += 1
        return count

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.get_full_name() + " (" + self.email + ")"


class Hospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=16)  # validators should be a list

    def formatted_phone(self):
        return "%s%s%s-%s%s%s-%s%s%s%s" % tuple(self.phone_number)

    def __str__(self):
        return self.name


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hospital = models.ForeignKey(Hospital)

    def __str__(self):
        return "Nurse " + self.user.get_full_name() + " (" + self.user.email + ")"

    def get_doctors(self):
        return self.doctor_set.all()


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hospitals = models.ManyToManyField(Hospital)
    max_patients = models.IntegerField()
    nurses = models.ManyToManyField(Nurse)

    def __str__(self):
        return "Dr. " + self.user.get_full_name() + " (" + self.user.email + ")"

    def get_hospitals(self):
        return self.hospitals.all()

    def get_nurses(self):
        return self.nurses.all()


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    insurance_number = models.CharField(max_length=13)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    blood_type = models.CharField(max_length=10, blank=True)
    hospital = models.ForeignKey(Hospital)
    doctor = models.ForeignKey(Doctor)
    isInHospital = models.BooleanField(default=False)
    isInTransit = models.BooleanField(default=False)
    emergency_first_name = models.CharField(max_length=30, blank=True)
    emergency_last_name = models.CharField(max_length=30, blank=True)
    emergency_phone_number = models.CharField(blank=True, max_length=16)
    emergency_address = models.CharField(max_length=200, blank=True)
    emergency_relationship = models.CharField(max_length=50, blank=True)

    def get_absolute_url(self):
        return reverse('patient:profile', kwargs={'pk': self.pk})

    def __str__(self):
        return self.user.get_full_name() + " (" + self.user.email + ")"

    def get_filtered_events(self):
        return self.event_set.order_by('date').reverse()

    def no_basic_info(self):
        no = (not self.emergency_first_name) or (not self.phone_number) or (not self.address) \
             or (not self.emergency_last_name) or (not self.emergency_address) \
             or (not self.emergency_phone_number) or (not self.emergency_relationship)
        return no

    def get_unapproved_tests_number(self):
        all_tests = self.testresult_set.all()
        ans = 0
        for test in all_tests:
            if test.is_released:
                ans += 1
        return ans


class H_Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hospital = models.ForeignKey(Hospital)

    def __str__(self):
        return "Admin " + self.user.get_full_name() + " (" + self.user.email + ")"


class Notification(models.Model):
    name = models.CharField(max_length=100, blank=False)
    recipient = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False, blank=False)


class AppointmentNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    appointment = models.IntegerField()


class PrescriptionNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)


class RemovedPrescriptionNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)


class TestResultNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)


class ApproveTestResultNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    test_result = models.IntegerField()


class ReceiveTransferNotification(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    transfer = models.IntegerField()


class HospitalStay(models.Model):
    REASON_CHOICES = (
        ('Infectious Disease', 'Infectious Disease'),
        ('Traumatic Injury', 'Traumatic Injury'),
        ('Poisoning/Drugs', 'Poisoning/Drugs'),
        ('Cardiac Issues', 'Cardiac Issues'),
        ('Chronic Illness', 'Chronic Illness'),
        ('Surgery', 'Surgery'),
        ('Other', 'Other'),
    )

    patient = models.ForeignKey(Patient)
    hospital = models.ForeignKey(Hospital)
    admission_date = models.DateField()
    discharge_date = models.DateField(blank=True, null=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    admission_details = models.CharField(blank=True, max_length=256)
    discharge_details = models.CharField(blank=True, max_length=256)
    admit_employee = models.ForeignKey(User, related_name='admit_employee')
    discharge_employee = models.ForeignKey(User, related_name='discharge_employee', blank=True, null=True)

    def __str__(self):
        return self.patient.user.first_name + " " + self.patient.user.last_name +\
               " was admitted to " + self.hospital.name + " for: " + self.reason


class OngoingTransfer(models.Model):
    patient = models.ForeignKey(Patient)
    dest_doctor = models.ForeignKey(Doctor, related_name='dest_doctor')
    dest_hospital = models.ForeignKey(Hospital, related_name='dest_hospital')
    src_doctor = models.ForeignKey(Doctor, related_name='src_doctor')
    src_hospital = models.ForeignKey(Hospital, related_name='src_hospital')