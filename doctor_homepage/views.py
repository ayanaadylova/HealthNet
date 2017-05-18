from django.shortcuts import render
from accounts.models import *
from appointment.models import Event, Patient
import datetime
import calendar
from django.core.urlresolvers import reverse_lazy
from appointment.forms import EventForm
from django.template.context_processors import csrf
from django.views.generic import DetailView, DeleteView, ListView, UpdateView, View
from log.models import EventLog, Log
from django.db.models import Q
from django.utils import timezone

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
            for day in week:
                if day == now:
                    day_events = [(day, Event.objects.filter(doctor=request.user.doctor, date=now).order_by('start_time'))]
                    events.append(day_events)
        args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = 'Daily'
        args['times'] = times
        return render(request, 'doctor_homepage/doctor_homepage.html', args)
    elif request.method == 'POST':
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
                for day in week:
                    if day == now:
                        day_events = [
                            (day, Event.objects.filter(doctor=request.user.doctor, date=now).order_by('start_time'))]
                        events.append(day_events)
            args = {'events': events, 'month': now.month, 'year': now.year, 'date': now, 'month_days': month_days}
            args.update(csrf(request))
            args['new_event_form'] = new_event_form
            args['calendar_view'] = 'Daily'
            args['times'] = times
            return render(request, 'doctor_homepage/doctor_homepage.html', args)

        month_days = cal.monthdatescalendar(year, month)

        if not request.POST['calendar_view']:
            calendar_view = 'Daily'
        else:
            calendar_view = request.POST['calendar_view']

        if calendar_view == 'Monthly':
            for week in month_days:
                week_events = [(day, Event.objects.filter(doctor=request.user.doctor, date=day).order_by('start_time')) for day in week]
                events.append(week_events)
        elif calendar_view == 'Weekly':
            for week in month_days:
                if chosen_day in week:
                    week_events = [(day, Event.objects.filter(doctor=request.user.doctor, date=day).order_by('start_time')) for day in week]
                    events.append(week_events)
        elif calendar_view == 'Daily':
            for week in month_days:
                for day in week:
                    if day == chosen_day:
                        day_events = [
                            (day, Event.objects.filter(doctor=request.user.doctor, date=day).order_by('start_time'))]
                        events.append(day_events)

        args = {'events': events, 'month': month, 'year': year, 'date': chosen_day, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = calendar_view
        args['times'] = times
        return render(request, 'doctor_homepage/doctor_homepage.html', args)
    return render(request, 'doctor_homepage/doctor_homepage.html')


def profile_view(request, pk):
    request.session['dash'] = None
    request.session['emr'] = None
    request.session['profile'] = 1
    request.session['messages'] = None

    template_name = 'doctor_homepage/profile.html'
    return render(request, template_name)


class UpdateUserInfo(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', ]
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('doctor:profile', args=[self.request.user.pk])


class EMRView(ListView):
    template_name = 'doctor_homepage/emr.html'
    context_object_name = 'patient_list'

    def get_queryset(self):
        self.request.session['dash'] = None
        self.request.session['emr'] = 1
        self.request.session['profile'] = None
        self.request.session['messages'] = None
        return Patient.objects.filter(doctor=self.request.user.doctor)


class EMRPatientView(DetailView):
    model = Patient
    template_name = 'doctor_homepage/patientemr.html'


def viewchronemr(request, pk):
    template_name = 'doctor_homepage/patient_chronemr.html'
    if request.method == 'GET':
        patient = Patient.objects.get(pk=pk)
        user = User.objects.get(pk=pk)
        log_list = Log.objects.filter(
            Q(subject=user, type='create') |
            Q(subject=user, type='admit') |
            Q(subject=user, type='discharge')
        ).order_by("-date_time")
        return render(request, template_name, {'patient': patient, 'log_list': log_list})


class DeleteEvent(DeleteView):
    model = Event

    def get_success_url(self):
        return reverse_lazy('doctor:index')

    # This makes it automatically delete when the function is called rather than redirect to a confirmation page
    # since there is already a popup to confirm the deletion
    def get(self, request, *args, **kwargs):
        event = Event.objects.get(pk=self.kwargs['pk'])
        appnotif = AppointmentNotification.objects.filter(appointment=event.pk)
        for notif in appnotif:
            notif.notification.delete()
            notif.delete()
        if event.patient is not None:
            log = Log.objects.create(
                date_time=timezone.now(),
                actor=request.user,
                hospital=event.patient.hospital,
                type='delete',
            )
        else:
            log = Log.objects.create(
                date_time=timezone.now(),
                actor=request.user,
                type='delete',
            )
        eventlog = EventLog.objects.create(
            log=log,
            doctor=event.doctor,
            eventtime=event.start_time,
            eventdate=event.date
        )
        if event.patient is not None:
            eventlog.patient = event.patient
            log.subject = event.patient.user
            log.description = ('Appointment for Doctor: ' + event.doctor.user.first_name + ' ' +
                               event.doctor.user.last_name + ' and Patient: ' + event.patient.user.first_name + ' ' +
                               event.patient.user.last_name+' at Date: '+event.date.strftime('%m/%d/%Y')+' and time: '+event.start_time.strftime('%I:%M %p') +
                               ' deleted')
        else:
            log.description = ('Personal Time for Doctor: ' + event.doctor.user.first_name + ' ' +
                               event.doctor.user.last_name + ' ' + event.date.strftime('%m/%d/%Y') + ' at' + event.start_time.strftime('%I:%M %p')+' deleted')
        log.save()
        return self.post(request, *args, **kwargs)
