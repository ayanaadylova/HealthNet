from django.shortcuts import render
import calendar
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.template.context_processors import csrf
from django.views.generic import UpdateView, View, DeleteView, ListView
from appointment.forms import *
from accounts.forms import *
from accounts.models import *
from prescription.models import *
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
            week_events = [(day, Event.objects.filter(patient=request.user.patient, date=day).order_by('start_time')) for day in week]
            events.append(week_events)
        args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = 'Monthly'
        args['times'] = times
        return render(request, 'patient_homepage/patient_homepage.html', args)
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
                week_events = [
                    (day, Event.objects.filter(patient=request.user.patient, date=day).order_by('start_time')) for day in week]
                events.append(week_events)
            args = {'events': events, 'month': now.month, 'year': now.year, 'date': now, 'month_days': month_days}
            args.update(csrf(request))
            args['new_event_form'] = new_event_form
            args['calendar_view'] = 'Monthly'
            args['times'] = times
            return render(request, 'patient_homepage/patient_homepage.html', args)

        month_days = cal.monthdatescalendar(year, month)

        if not request.POST['calendar_view']:
            calendar_view = 'Monthly'
        else:
            calendar_view = request.POST['calendar_view']

        if calendar_view == 'Monthly':
            for week in month_days:
                week_events = [(day, Event.objects.filter(patient=request.user.patient, date=day).order_by('start_time')) for day in week]
                events.append(week_events)
        elif calendar_view == 'Weekly':
            for week in month_days:
                if chosen_day in week:
                    week_events = [(day, Event.objects.filter(patient=request.user.patient, date=day).order_by('start_time')) for day in week]
                    events.append(week_events)
        elif calendar_view == 'Daily':
            for week in month_days:
                for day in week:
                    if day == chosen_day:
                        week_events = [(day, Event.objects.filter(patient=request.user.patient, date=day).order_by('start_time'))]
                        events.append(week_events)
        doctor_events = Event.objects.filter(doctor=request.user.patient.doctor, date=chosen_day).exclude(patient=request.user.patient)
        args = {'events': events, 'month': month, 'year': year, 'date': chosen_day, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = calendar_view
        args['times'] = times
        args['doctor_events'] = doctor_events
        return render(request, 'patient_homepage/patient_homepage.html', args)
    return render(request, 'patient_homepage/patient_homepage.html')


class ExtraInfoFormView(View):
    form_class = ExtraInfoForm
    template_name = 'accounts/extra_info_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            patient = request.user.patient
            patient.address = form.cleaned_data['address']
            patient.phone_number = form.cleaned_data['phone_number']
            patient.emergency_first_name = form.cleaned_data['emergency_first_name']
            patient.emergency_last_name = form.cleaned_data['emergency_last_name']
            patient.emergency_phone_number = form.cleaned_data['emergency_phone_number']
            patient.emergency_address = form.cleaned_data['emergency_address']
            patient.emergency_relationship = form.cleaned_data['emergency_relationship']

            patient.save()
            return HttpResponseRedirect(reverse('patient:index'))

        return render(request, self.template_name, {'form': form})


def viewemr(request):
    request.session['dash'] = None
    request.session['emr'] = 1
    request.session['profile'] = None
    request.session['messages'] = None
    for pres in request.user.patient.prescription_set.all():
        if pres.end_date <= datetime.date.today():
            pres.removed = True
            pres.save()
    return render(request, 'patient_homepage/emr.html')


class EMRChronView(ListView):
    model = Log
    template_name = 'patient_homepage/chronemr.html'

    def get_queryset(self):
        self.request.session['dash'] = None
        self.request.session['emr'] = 1
        self.request.session['profile'] = None
        self.request.session['messages'] = None
        log_list = Log.objects.filter(
            Q(subject=self.request.user, type='create') |
            Q(subject=self.request.user, type='update') |
            Q(subject=self.request.user, type='admit') |
            Q(subject=self.request.user, type='discharge')
        ).order_by("-date_time")
        return log_list


class UpdateUserInfo(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', ]
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('patient:update2', kwargs={'pk': self.kwargs['pk']})


class UpdatePatientInfo(UpdateView):
    model = Patient
    fields = ['address', 'phone_number', 'emergency_first_name', 'emergency_last_name', 'emergency_phone_number',
              'emergency_address', 'emergency_relationship']

    def get_success_url(self):
        return reverse('accounts:patientprofile',  kwargs={'pk': self.kwargs['pk']})


class DeleteEvent(DeleteView):
    model = Event

    def get_success_url(self):
        return reverse_lazy('patient:index')

    # This makes it automatically delete when the function is called rather than redirect to a confirmation page
    # since there is already a popup to confirm the deletion
    def get(self, request, *args, **kwargs):
        event = Event.objects.get(pk=self.kwargs['pk'])
        appnotif = AppointmentNotification.objects.filter(appointment=event.pk)
        for notif in appnotif:
            notif.notification.delete()
            notif.delete()
        log = Log.objects.create(
            date_time=timezone.now(),
            actor=request.user,
            subject=request.user,
            hospital=request.user.patient.hospital,
            type='delete',
            description=('Patient '+event.patient.user.get_full_name() +
                         ' deleted Appointment on '+datetime.date.today().__str__())
        )
        eventlog = EventLog.objects.create(
            log=log,
            eventdate=event.date,
            eventtime=event.start_time,
            doctor=event.patient.doctor,
            patient=event.patient
        )

        return self.post(request, *args, **kwargs)
