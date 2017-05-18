from django.db import models
import datetime
from accounts.models import Patient, Doctor
from datetime import date


class Event(models.Model):
    START_TIME_CHOICES = (
        (datetime.time(9, 00), '9:00am'),
        (datetime.time(9, 30), '9:30am'),
        (datetime.time(10, 0), '10:00am'),
        (datetime.time(10, 30), '10:30am'),
        (datetime.time(11, 0), '11:00am'),
        (datetime.time(11, 30), '11:30am'),
        (datetime.time(12, 0), '12:00pm'),
        (datetime.time(12, 30), '12:30pm'),
        (datetime.time(13, 0), '1:00pm'),
        (datetime.time(13, 30), '1:30pm'),
        (datetime.time(14, 0), '2:00pm'),
        (datetime.time(14, 30), '2:30pm'),
        (datetime.time(15, 0), '3:00pm'),
        (datetime.time(15, 30), '3:30pm'),
        (datetime.time(16, 0), '4:00pm'),
        (datetime.time(16, 30), '4:30pm'),
    )
    END_TIME_CHOICES = (
        (datetime.time(9, 30), '9:30am'),
        (datetime.time(10, 0), '10:00am'),
        (datetime.time(10, 30), '10:30am'),
        (datetime.time(11, 0), '11:00am'),
        (datetime.time(11, 30), '11:30am'),
        (datetime.time(12, 0), '12:00pm'),
        (datetime.time(12, 30), '12:30pm'),
        (datetime.time(13, 0), '1:00pm'),
        (datetime.time(13, 30), '1:30pm'),
        (datetime.time(14, 0), '2:00pm'),
        (datetime.time(14, 30), '2:30pm'),
        (datetime.time(15, 0), '3:00pm'),
        (datetime.time(15, 30), '3:30pm'),
        (datetime.time(16, 0), '4:00pm'),
        (datetime.time(16, 30), '4:30pm'),
        (datetime.time(17, 0), '5:00pm'),
    )
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(choices=START_TIME_CHOICES)
    end_time = models.TimeField(choices=END_TIME_CHOICES)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    def happened(self):
        today = datetime.datetime.today()
        if self.date < date.today():
            return True
        elif self.date == date.today() and self.end_time <= datetime.time(hour=today.hour, minute=today.minute, second=today.second):
            return True
        else:
            return False

