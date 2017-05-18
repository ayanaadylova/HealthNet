from django.db import models
from accounts.models import *


class Log(models.Model):
    date_time = models.DateTimeField(null=True)
    actor = models.ForeignKey(User, related_name="log_actor", null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(User, null=True, related_name="log_subject", blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=256, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, null=True, on_delete=models.SET_NULL)
    types = (
        ('create', 'create'),
        ('delete', 'delete'),
        ('update', 'update'),
        ('admit', 'admit'),
        ('discharge', 'discharge'),
    )

    type = models.CharField(max_length=25, choices=types)


class PrescLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    drugname = models.CharField(max_length=50)
    dosage = models.CharField(max_length=15)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    refills = models.IntegerField(default=0)


class AdmissionLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    reason = models.CharField(max_length=50)


class TransferLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    prevhospital = models.ForeignKey(Hospital, null=True, related_name='previous_hospital', on_delete=models.SET_NULL)
    destination = models.ForeignKey(Hospital, null=True, on_delete=models.SET_NULL)
    prevdoctor = models.ForeignKey(Doctor, null=True, related_name='previous_doctor', on_delete=models.SET_NULL)
    newdoctor = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)


class TestResultLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    date = models.DateField(null=True)
    name = models.CharField(max_length=100)
    information = models.CharField(max_length=2500)
    file = models.FileField(blank=True, null=True)
    is_released = models.BooleanField()


class MessageLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    message = models.CharField(max_length=256)


class EventLog(models.Model):
    log = models.OneToOneField(Log, primary_key=True, on_delete=models.PROTECT)
    eventdate = models.DateField()
    eventtime = models.TimeField()
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    patient = models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)

