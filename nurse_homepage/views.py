from accounts.models import *
from appointment.models import Event
from django.shortcuts import render
import datetime
import calendar
from appointment.forms import EventForm
from django.template.context_processors import csrf
from django.views.generic import DetailView, UpdateView, ListView
from log.models import Log
from django.db.models import Q


def index(request):
    request.session['dash'] = 1
    request.session['emr'] = None
    request.session['profile'] = None
    request.session['messages'] = None

    request.session['name'] = None
    request.session['date'] = None
    request.session['start_time'] = None
    request.session['patient'] = None
    request.session['doctor'] = None
    new_event_form = EventForm()
    now = datetime.date.today()
    year = now.year
    month = now.month
    cal = calendar.Calendar(calendar.SUNDAY)
    month_days = cal.monthdatescalendar(year, month)

    events = []
    times = [datetime.time(9, 00),
             datetime.time(9, 30),
             datetime.time(10, 00),
             datetime.time(10, 30),
             datetime.time(11, 00),
             datetime.time(11, 30),
             datetime.time(12, 00),
             datetime.time(12, 30),
             datetime.time(13, 00),
             datetime.time(13, 30),
             datetime.time(14, 00),
             datetime.time(14, 30),
             datetime.time(15, 00),
             datetime.time(15, 30),
             datetime.time(16, 00),
             datetime.time(16, 30),
             datetime.time(17, 00)]
    if request.method == 'GET':
        for week in month_days:
            if now in week:
                weekly_events = []
                for day in week:
                    weekly_events.append((day, []))
                events.append(weekly_events)
        args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = 'Weekly'
        args['doctors'] = request.user.nurse.doctor_set.all()
        patients = []
        for doctor in request.user.nurse.doctor_set.all():
            for patient in doctor.patient_set.all():
                if patient.hospital == request.user.nurse.hospital:
                    patients.append(patient)
        args['patients'] = patients
        args['times'] = times
        return render(request, 'nurse_homepage/nurse_homepage.html', args)
    elif request.method == 'POST':
        if not request.POST['calendar_view']:
            calendar_view = 'Weekly'
        else:
            calendar_view = request.POST['calendar_view']

        if request.POST['dob_month']:
            month = int(request.POST['dob_month'])
        if request.POST['dob_year']:
            year = int(request.POST['dob_year'])
        if request.POST['dob_day']:
            day = int(request.POST['dob_day'])
            chosen_day = day
        else:
            chosen_day = now.day

        try:
            chosen_day = datetime.date(year, month, chosen_day)
        except ValueError:
            for week in month_days:
                if now in week:
                    weekly_events = []
                    for day in week:
                        weekly_events.append((day, []))
                    events.append(weekly_events)
            args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
            args.update(csrf(request))
            args['new_event_form'] = new_event_form
            args['calendar_view'] = 'Weekly'
            args['doctors'] = request.user.nurse.doctor_set.all()
            patients = []
            for doctor in request.user.nurse.doctor_set.all():
                for patient in doctor.patient_set.all():
                    if patient.hospital == request.user.nurse.hospital:
                        patients.append(patient)
            args['patients'] = patients
            args['times'] = times
            return render(request, 'nurse_homepage/nurse_homepage.html', args)

        month_days = cal.monthdatescalendar(year, month)

        chosen_doctor = None
        chosen_patient = None
        if request.POST['chosen_doctor']:
            chosen_doctor = Doctor.objects.get(pk=request.POST['chosen_doctor'])
        if request.POST['chosen_patient']:
            chosen_patient = Patient.objects.get(pk=request.POST['chosen_patient'])

        if (not chosen_doctor and not chosen_patient) or (chosen_doctor and chosen_patient):
            if calendar_view == 'Monthly':
                for week in month_days:
                    weekly_events = []
                    for day in week:
                        weekly_events.append((day, []))
                    events.append(weekly_events)
            elif calendar_view == 'Weekly':
                for week in month_days:
                    if chosen_day in week:
                        weekly_events = []
                        for day in week:
                            weekly_events.append((day, []))
                        events.append(weekly_events)
            elif calendar_view == 'Daily':
                for week in month_days:
                    weekly_events = []
                    for day in week:
                        if chosen_day == day:
                            weekly_events.append((day, []))
                    events.append(weekly_events)

        if chosen_doctor and not chosen_patient:
            if calendar_view == 'Monthly':
                for week in month_days:
                    weekly_events = []
                    for day in week:
                        events_for_one_day = []
                        events_for_doctor = Event.objects.filter(doctor=chosen_doctor, date=day).order_by('start_time')
                        for event in events_for_doctor:
                            if event.patient:
                                # if event.patient.hospital == request.user.nurse.hospital:
                                    events_for_one_day.append(event)
                        weekly_events.append((day, events_for_one_day))
                    events.append(weekly_events)
            elif calendar_view == 'Weekly':
                for week in month_days:
                    if chosen_day in week:
                        weekly_events = []
                        for day in week:
                            events_for_one_day = []
                            events_for_doctor = Event.objects.filter(doctor=chosen_doctor, date=day).order_by('start_time')
                            for event in events_for_doctor:
                                if event.patient:
                                    # if event.patient.hospital == request.user.nurse.hospital:
                                        events_for_one_day.append(event)
                            weekly_events.append((day, events_for_one_day))
                        events.append(weekly_events)
            elif calendar_view == 'Daily':
                for week in month_days:
                    weekly_events = []
                    for day in week:
                        if day == chosen_day:
                            events_for_one_day = []
                            events_for_doctor = Event.objects.filter(doctor=chosen_doctor, date=day).order_by('start_time')
                            for event in events_for_doctor:
                                if event.patient:
                                    # if event.patient.hospital == request.user.nurse.hospital:
                                        events_for_one_day.append(event)
                            weekly_events.append((day, events_for_one_day))
                    events.append(weekly_events)

        if chosen_patient and not chosen_doctor:
            if calendar_view == 'Monthly':
                for week in month_days:
                    week_events = [
                        (day, Event.objects.filter(patient=chosen_patient, date=day).order_by('start_time')) for
                        day in week]
                    events.append(week_events)
            elif calendar_view == 'Weekly':
                for week in month_days:
                    if chosen_day in week:
                        week_events = [
                            (day, Event.objects.filter(patient=chosen_patient, date=day).order_by('start_time'))
                            for day in week]
                        events.append(week_events)
            elif calendar_view == 'Daily':
                for week in month_days:
                    for day in week:
                        if day == chosen_day:
                            week_events = [(day, Event.objects.filter(patient=chosen_patient, date=day).order_by(
                                'start_time'))]
                            events.append(week_events)

        args = {'events': events, 'month': month, 'year': year, 'date': chosen_day, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = calendar_view
        args['doctors'] = request.user.nurse.doctor_set.all()
        patients = []
        for doctor in request.user.nurse.doctor_set.all():
            for patient in doctor.patient_set.all():
                if patient.hospital == request.user.nurse.hospital:
                    patients.append(patient)
        args['patients'] = patients
        args['times'] = times
        if chosen_patient and not chosen_doctor:
            args['chosen_patient'] = chosen_patient
            if calendar_view == 'Daily':
                doctor_events = Event.objects.filter(doctor=chosen_patient.doctor, date=chosen_day).exclude(
                    patient=chosen_patient)
                args['doctor_events'] = doctor_events
        if chosen_doctor and not chosen_patient:
            args['chosen_doctor'] = chosen_doctor
            if calendar_view == 'Daily':
                doctor_events = Event.objects.filter(patient=None, date=chosen_day)
                args['doctor_events'] = doctor_events
        return render(request, 'nurse_homepage/nurse_homepage.html', args)
    return render(request, 'nurse_homepage/nurse_homepage.html')


class EMRView(ListView):
    template_name = 'nurse_homepage/emr.html'
    context_object_name = 'patient_list'

    def get_queryset(self):
        self.request.session['dash'] = None
        self.request.session['emr'] = 1
        self.request.session['profile'] = None
        self.request.session['messages'] = None
        return Patient.objects.filter(doctor__in=self.request.user.nurse.doctor_set.all(), hospital=self.request.user.nurse.hospital)


class EMRPatientView(DetailView):
    model = Patient
    template_name = 'nurse_homepage/patientemr.html'


def viewchronemr(request, pk):
    template_name = 'nurse_homepage/patient_chronemr.html'
    if request.method == 'GET':
        patient = Patient.objects.get(pk=pk)
        user = User.objects.get(pk=pk)
        log_list = Log.objects.filter(
            Q(subject=user, type='create') |
            Q(subject=user, type='admit') |
            Q(subject=user, type='discharge')
        ).order_by("-date_time")
        return render(request, template_name, {'patient': patient, 'log_list': log_list})


def profile_view(request, pk):
    request.session['dash'] = None
    request.session['emr'] = None
    request.session['profile'] = 1
    request.session['messages'] = None

    template_name = 'nurse_homepage/profile.html'
    return render(request, template_name)


class UpdateUserInfo(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', ]
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('nurse:profile', args=[self.request.user.pk])
