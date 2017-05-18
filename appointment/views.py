from django.shortcuts import render
from django.views.generic import View, DetailView
from django.http import HttpResponseRedirect
from log.models import *
from .forms import *
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone


class EventDetail(DetailView):
    model = Event
    template = 'appointment/event_detail.html'


class MakeAppointmentChooseDoctor(View):
    form_class = EventFormChooseDoctor
    template_name = 'appointment/makeappointmentchoosedoctor.html'

    def get(self, request):
        initial = {'doctor': request.session.get('doctor', None)}
        form = self.form_class(user=request.user, initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'doctor': request.session.get('doctor', None)}
        form = self.form_class(request.POST, user=request.user, initial=initial)
        if form.is_valid():
            request.session['doctor'] = form.cleaned_data['doctor'].pk
            return HttpResponseRedirect(reverse('appointment:makeappointmentdate'))
        return render(request, self.template_name, {'form': form})


class MakeAppointmentDateDoctor(View):
    template_name = 'appointment/makeappointmentdate.html'
    form_class = EventFormDateStaff

    def get(self, request):
        initial = {'name': request.session.get('name', None),
                   'patient': request.session.get('patient', None),
                   }
        if request.session.get('date') is not None:
            initial['date'] = request.session.get('date', None)
        else:
            initial['date'] = timezone.now()

        form = self.form_class(user=request.user, userpk=request.user.pk, initial=initial)
        request.session['doctor'] = request.user.pk
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'name': request.session.get('name', None),
                   'patient': request.session.get('patient', None),
                   'date': request.session.get('date', None),
                   }
        form = self.form_class(request.POST, user=request.user, userpk=request.session['doctor'], initial=initial)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            request.session['date'] = form.cleaned_data['date'].isoformat()
            if form.cleaned_data['patient']:
                request.session['patient'] = form.cleaned_data['patient'].pk
            else:
                request.session['patient'] = None
            return HttpResponseRedirect(reverse('appointment:makeappointmenttime'))
        return render(request, self.template_name, {'form': form})


class MakeAppointmentDate(View):
    template_name = 'appointment/makeappointmentdate.html'

    def get(self, request):

        if Nurse.objects.filter(pk=request.user.pk).exists() or H_Admin.objects.filter(pk=request.user.pk).exists():
            initial = {'name': request.session.get('name', None),
                       'patient': request.session.get('patient', None),
                       }
            if request.session.get('date') is not None:
                initial['date'] = request.session.get('date', None)
            else:
                initial['date'] = timezone.now()
            form_class = EventFormDateStaff
            form = form_class(user=request.user, userpk=request.session['doctor'], initial=initial)

        elif Patient.objects.filter(pk=request.user.pk).exists():
            initial = {'name': request.session.get('name', None) }
            if request.session.get('date') is not None:
                initial['date'] = request.session.get('date', None)
            else:
                initial['date'] = timezone.now()
            form_class = EventFormDatePatient
            form = form_class(None, initial=initial)
            request.session['doctor'] = request.user.patient.doctor.pk

        else:  # Doctor
            initial = {'name': request.session.get('name', None),
                       'patient': request.session.get('patient', None),
                       }
            if request.session.get('date') is not None:
                initial['date'] = request.session.get('date', None)
            else:
                initial['date'] = timezone.now()
            form_class = EventFormDateStaff
            form = form_class(user=request.user, userpk=request.user.pk, initial=initial)
            request.session['doctor'] = request.user.pk
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if hasattr(request.user, 'patient'):
            initial = {'name': request.session.get('name', None),
                       'date': request.session.get('date', None),
                       }
            form_class = EventFormDatePatient
            form = form_class(request.POST, initial=initial)
        else:
            initial = {'name': request.session.get('name', None),
                       'patient': request.session.get('patient', None),
                       'date': request.session.get('date', None),
                       }
            form_class = EventFormDateStaff
            form = form_class(request.POST, user=request.user, userpk=request.session['doctor'], initial=initial)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            request.session['date'] = form.cleaned_data['date'].isoformat()
            if not hasattr(request.user, 'patient'):
                if form.cleaned_data['patient']:
                    request.session['patient'] = form.cleaned_data['patient'].pk
                else:
                    request.session['patient'] = None
            return HttpResponseRedirect(reverse('appointment:makeappointmenttime'))
        return render(request, self.template_name, {'form': form})


class MakeAppointmentTime(View):
    form_class = EventFormTime
    template_name = 'appointment/makeappointmenttime.html'

    def get(self, request):
        initial = {'start_time': request.session.get('start_time', None)}
        form = self.form_class(user=Doctor.objects.get(pk=request.session['doctor']), day=request.session['date'], initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_staff:
            initial = {'start_time': request.session.get('start_time', None)}
            form = self.form_class(request.POST, user=None, day=None, initial=initial)
            if form.is_valid():
                request.session['start_time'] = form.cleaned_data['start_time'].isoformat()
                return HttpResponseRedirect(reverse('appointment:makeappointmentendtime'))
        else:
            form = self.form_class(request.POST, user=None, day=None)
            if form.is_valid():
                patient = request.user.patient
                doctor = patient.doctor
                name = request.session['name']
                date = request.session['date']
                start_time = form.cleaned_data['start_time']
                end_time = (datetime.datetime(2000, 1, 1, hour=start_time.hour, minute=start_time.minute,
                                              second=start_time.second) + datetime.timedelta(minutes=30)).time()
                event = Event.objects.create(patient=patient,
                                             doctor=doctor,
                                             name=name,
                                             date=date,
                                             start_time=start_time,
                                             end_time=end_time)
                log = Log.objects.create(
                    date_time=timezone.now(),
                    actor=request.user,
                    subject=patient.user,
                    hospital=patient.hospital,
                    type='create',
                    description='Appointment for Doctor: ' + doctor.user.get_full_name() + ' and Patient: ' +
                                patient.user.get_full_name() + ' created for: ' + date + ' at: ' + start_time.strftime('%I:%M %p'),
                )
                EventLog.objects.create(
                    log=log,
                    patient=patient,
                    doctor=doctor,
                    eventtime=start_time,
                    eventdate=date
                )
                return HttpResponseRedirect(reverse('patient:index'))
        return render(request, self.template_name, {'form': form})


class MakeAppointmentEndTime(View):
    form_class = EventFormEndTime
    template_name = 'appointment/makeappointmentendtime.html'

    def get(self, request):
        form = self.form_class(user=Doctor.objects.get(pk=request.session['doctor']),
                               day=request.session['date'],
                               start_time=request.session['start_time'])
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, user=None, day=None, start_time=None)
        if form.is_valid():
            if request.session['patient']:
                patient = Patient.objects.get(pk=request.session['patient'])
                hospital = patient.hospital
            else:
                patient = None
            if hasattr(request.user, 'nurse') or hasattr(request.user, 'h_admin'):
                doctor = Doctor.objects.get(pk=request.session['doctor'])
                if hasattr(request.user, 'nurse'):
                    hospital = request.user.nurse.hospital
                else:
                    hospital = request.user.h_admin.hospital
            else:
                doctor = request.user.doctor
                hospital = None
            name = request.session['name']
            date = request.session['date']
            start_time = request.session['start_time']
            end_time = form.cleaned_data['end_time']
            event = Event.objects.create(patient=patient,
                                         doctor=doctor,
                                         name=name,
                                         date=date,
                                         start_time=start_time,
                                         end_time=end_time)
            if patient:
                notification = Notification.objects.create(
                    name="You have a new appointment/event scheduled",
                    recipient=patient.user,
                )
                AppointmentNotification.objects.create(
                    notification=notification,
                    appointment=event.pk,
                )
            log = Log.objects.create(
                date_time=timezone.now(),
                actor=request.user,
                hospital=hospital,
                type='create',
            )
            eventlog = EventLog.objects.create(
                log=log,
                doctor=doctor,
                eventtime=start_time,
                eventdate=date,
            )
            if patient is not None:
                eventlog.patient = patient
                log.subject = patient.user
                log.description = ('Appointment for Doctor: ' + doctor.user.get_full_name() +
                                   ' and Patient: ' + patient.user.get_full_name() + ' at Date: ' + date +
                                   ' and Time: ' + start_time)
            else:
                log.description = ('Doctor: ' + doctor.user.get_full_name() + ' created personal event at Date: ' +
                                   date + ' and Time: ' + start_time)
            log.save()
            eventlog.save()
            if Doctor.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('doctor:index'))
            elif Nurse.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('nurse:index'))
            elif H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:index'))
        return render(request, self.template_name, {'form': form})


class UpdateEventDate(View):
    form_class = EventFormDatePatient
    template_name = 'appointment/updateappointmentdate.html'

    def get(self, request, pk):
        event = Event.objects.get(pk=pk)
        initial = {'name': event.name,
                   'date': event.date,
                   }
        if request.session.get('name') is not None and request.session.get('date') is not None:
            initial['date'] = request.session.get('date', None)
            initial['name'] = request.session.get('name', None)
        form = self.form_class(None, initial=initial)
        return render(request, self.template_name, {'form': form, 'pk': pk})

    def post(self, request, pk):
        initial = {'name': request.session.get('name', None),
                   'date': request.session.get('date', None),
                   }
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            request.session['date'] = form.cleaned_data['date'].isoformat()
            event = Event.objects.get(pk=pk)
            request.session['doctor'] = event.doctor.pk
            return HttpResponseRedirect(reverse('appointment:updateevent2', kwargs={'pk': pk}))
        return render(request, self.template_name, {'form': form, 'pk': pk})


class UpdateEventTime(View):
    form_class = EventFormTime
    template_name = 'appointment/updateappointmenttime.html'

    def get(self, request, pk):
        event = Event.objects.get(pk=pk)
        initial = {'start_time': event.start_time}
        if request.session.get('start_time') is not None:
            initial['start_time'] = request.session.get('start_time')
        form = self.form_class(user=Doctor.objects.get(pk=request.session['doctor']), day=request.session['date'], initial=initial)
        return render(request, self.template_name, {'form': form, 'pk':pk})

    def post(self, request, pk):
        initial = {'start_time': request.session.get('start_time', None)}
        form = self.form_class(request.POST, user=Doctor.objects.get(pk=request.session['doctor']), day=request.session['date'], initial=initial)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            if request.user.is_staff:
                request.session['start_time'] = start_time
                return HttpResponseRedirect(reverse('appointment:updateevent3', kwargs={'pk': pk}))

            elif hasattr(request.user, 'patient'):
                name = request.session['name']
                date = request.session['date']
                end_time = (datetime.datetime(2000, 1, 1, hour=start_time.hour, minute=start_time.minute, second=start_time.second) + datetime.timedelta(minutes=30)).time()
                event = Event.objects.get(pk=pk)
                event.name = name
                event.date = date
                event.start_time = start_time
                event.end_time = end_time
                event.save()
                log = Log.objects.create(
                    date_time=timezone.now(),
                    actor=request.user,
                    subject=event.patient.user,
                    hospital=event.patient.hospital,
                    type='update',
                    description=('Appointment for Doctor: ' + event.doctor.user.get_full_name() + ' and Patient: ' +
                                 request.user.get_full_name() + ' updated to Date: ' + date + ' at Time: ' + start_time.strftime('%I%M%p'))
                )
                EventLog.objects.create(
                    log=log,
                    doctor=event.doctor,
                    patient=event.patient,
                    eventtime=start_time,
                    eventdate=date,
                )
                return HttpResponseRedirect(reverse('patient:index'))

        return render(request, self.template_name, {'form': form})


class UpdateEventEndTime(View):
    form_class = EventFormEndTime
    template_name = 'appointment/updateappointmentendtime.html'

    def get(self, request, pk):
        form = self.form_class(user=Doctor.objects.get(pk=request.session['doctor']), day=request.session['date'],
                               start_time=request.session['start_time'])
        return render(request, self.template_name, {'form': form, 'pk':pk})

    def post(self, request, pk):
        form = self.form_class(request.POST, user=None, day=None, start_time=None)
        if form.is_valid():
            name = request.session['name']
            date = request.session['date']
            start_time = request.session['start_time']
            end_time = form.cleaned_data['end_time']
            event = Event.objects.get(pk=pk)
            event.name = name
            event.date = date
            event.start_time = start_time
            event.end_time = end_time
            event.save()
            if event.patient is not None:
                log = Log.objects.create(
                    date_time=timezone.now(),
                    actor=request.user,
                    hospital=event.patient.hospital,
                    type='update',
                )
            else:
                log = Log.objects.create(
                    date_time=timezone.now(),
                    actor=request.user,
                    type='update',
                )
            eventlog = EventLog.objects.create(
                log=log,
                doctor=event.doctor,
                eventtime=start_time,
                eventdate=date
            )
            if event.patient is not None:
                eventlog.patient = event.patient
                log.subject = event.patient.user
                log.description = ('Appointment for Doctor: ' + event.doctor.user.first_name + ' ' +
                                        event.doctor.user.last_name+' and Patient: ' + event.patient.user.first_name + ' ' +
                                        event.patient.user.last_name+' at Date:'+date+' and time: ' + start_time)
            else:
                log.description = ('Personal Time for Doctor: ' + event.doctor.user.get_full_name() + ' updated to '
                                   + date + ' at ' + start_time)
            log.save()
            eventlog.save()
            log.save()
            if Doctor.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('doctor:index'))
            elif Nurse.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('nurse:index'))
            elif H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:index'))
        return render(request, self.template_name, {'form': form})


class EventNotificationHandler(View):

    def get(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        try:
            return HttpResponseRedirect(reverse_lazy('appointment:eventdetail', kwargs={'pk': notification.appointmentnotification.appointment}))
        finally:
            notification.delete()


class MakeCalendarAppointment(View):
    template_name = 'appointment/calendarappointment.html'

    def get(self, pk, request):
        return render(request, self.template_name)



