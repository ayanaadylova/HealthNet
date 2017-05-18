from django import forms
from .models import Event
from django.utils import timezone
from django.forms import ModelForm, ValidationError
import datetime
from accounts.models import User, Doctor
from django.forms.extras.widgets import SelectDateWidget


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = (
            'name',
            'date',
            'start_time',
            'end_time'
        )


class EventFormChooseDoctor(ModelForm):

    class Meta:
        model = Event
        fields = (
            'doctor',
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(EventFormChooseDoctor, self).__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'nurse'):
                self.fields['doctor'] = forms.ModelChoiceField(queryset=user.nurse.doctor_set.all())
            else:
                self.fields['doctor'] = forms.ModelChoiceField(queryset=user.h_admin.hospital.doctor_set.all())


class EventFormDatePatient(ModelForm):
    date = forms.DateField(widget=SelectDateWidget, initial=timezone.now())

    class Meta:
        model = Event
        fields = (
            'name',
            'date',
        )

    def clean_date(self):
        date = self.cleaned_data['date']
        today = datetime.date.today()
        if date < today:
            raise ValidationError("You can't make an appointment in the past")
        if date == today:
            curr_time = timezone.now().time()
            last_time = datetime.time(21, 30)
            if curr_time > last_time:
                raise ValidationError("There are no more available appointment times for today")
        return date


class EventFormDateStaff(ModelForm):

    def __init__(self, *args, **kwargs):
        userpk = kwargs.pop('userpk')
        user = kwargs.pop('user')
        super(EventFormDateStaff, self).__init__(*args, **kwargs)
        if User.objects.filter(pk=userpk):
            doc = Doctor.objects.get(pk=userpk)
            if hasattr(user, 'nurse'):
                self.fields['patient'] = forms.ModelChoiceField(queryset=doc.patient_set.filter(
                    hospital=user.nurse.hospital))
            elif hasattr(user, 'doctor'):
                self.fields['patient'] = forms.ModelChoiceField(queryset=doc.patient_set.all(), required=False)
            else:
                self.fields['patient'] = forms.ModelChoiceField(queryset=doc.patient_set.filter(
                    hospital=user.h_admin.hospital))

    date = forms.DateField(widget=SelectDateWidget, initial=timezone.now())

    class Meta:
        model = Event
        fields = (
            'name',
            'patient',
            'date',
        )

    def clean_date(self):
        date = self.cleaned_data['date']
        today = datetime.date.today()
        if date < today:
            raise ValidationError("You can't make an appointment in the past")
        if date == today:
            curr_time = timezone.now().time()
            last_time = datetime.time(21, 30)
            if curr_time > last_time:
                raise ValidationError("There are no more available appointment times for today")
        return date


class EventFormTime(ModelForm):

    class Meta:
        model = Event
        fields = (
            'start_time',
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        day = kwargs.pop('day')
        super(EventFormTime, self).__init__(*args, **kwargs)
        if user and day:
            All_START_TIME_CHOICES = [
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
            ]
            START_TIME_CHOICES = []
            events_for_day = Event.objects.filter(doctor=user, date=day)
            for choice in All_START_TIME_CHOICES:
                choice_doesnt_intersect = True
                for event in events_for_day:
                    if choice[0]<event.end_time and choice[0]>=event.start_time:
                        choice_doesnt_intersect = False
                        break
                if choice_doesnt_intersect:
                    now = datetime.datetime.now()
                    if day == datetime.date(now.year,now.month,now.day).isoformat():
                        if choice[0] > now.time():
                            START_TIME_CHOICES.append(choice)
                    else:
                        START_TIME_CHOICES.append(choice)
            self.fields['start_time'] = forms.ChoiceField(
                choices=START_TIME_CHOICES
            )


class EventFormEndTime(ModelForm):

    class Meta:
        model = Event
        fields = (
            'end_time',
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        day = kwargs.pop('day')
        start_time = kwargs.pop('start_time')
        super(EventFormEndTime, self).__init__(*args, **kwargs)
        if user and day:
            All_END_TIME_CHOICES = [
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
            ]
            END_TIME_CHOICES = []
            if user.user.is_staff:
                events_for_day = Event.objects.filter(doctor=user, date=day)
            else:
                events_for_day = Event.objects.filter(doctor=user.doctor, date=day)
            start_time = datetime.datetime.strptime('07/28/2014 '+start_time, '%m/%d/%Y %H:%M:%S').time()
            for choice in All_END_TIME_CHOICES:
                if choice[0] > start_time:
                    choice_doesnt_intersect = True
                    for event in events_for_day:
                        if choice[0]<=event.end_time and choice[0]>event.start_time:
                            choice_doesnt_intersect = False
                            break
                    if choice_doesnt_intersect:
                        END_TIME_CHOICES.append(choice)
                    else:
                        break
            self.fields['end_time'] = forms.ChoiceField(
                choices=END_TIME_CHOICES
            )