from django.shortcuts import render
from django.views.generic import DetailView, View, ListView, UpdateView, DeleteView
from appointment.models import Event
from appointment.forms import EventForm
import datetime
from django.utils import timezone
import calendar
from django.template.context_processors import csrf
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from .forms import *
from io import TextIOWrapper
from prescription.models import Prescription
from collections import OrderedDict
from healthnet.views import load_csv
from log.models import *
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

    request.session['email'] = None
    request.session['first_name'] = None
    request.session['last_name'] = None
    request.session['password'] = None
    request.session['usertype'] = None
    request.session['hospitals'] = None
    request.session['max_patients'] = None
    request.session['nurses'] = None
    request.session['hospital'] = None
    request.session['doctors'] = None

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
                    if day == now:
                        weekly_events.append((day, []))
                events.append(weekly_events)
        args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
        args.update(csrf(request))
        args['new_event_form'] = new_event_form
        args['calendar_view'] = 'Daily'
        args['doctors'] = request.user.h_admin.hospital.doctor_set.all()
        args['patients'] = Patient.objects.filter(hospital=request.user.h_admin.hospital)
        args['times'] = times
        return render(request, 'h_admin_homepage/h_admin_homepage.html', args)
    elif request.method == 'POST':
        if not request.POST['calendar_view']:
            calendar_view = 'Daily'
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
                        if day == now:
                            weekly_events.append((day, []))
                    events.append(weekly_events)
            args = {'events': events, 'month': month, 'year': year, 'date': now, 'month_days': month_days}
            args.update(csrf(request))
            args['new_event_form'] = new_event_form
            args['calendar_view'] = 'Daily'
            args['doctors'] = request.user.h_admin.hospital.doctor_set.all()
            args['patients'] = Patient.objects.filter(hospital=request.user.h_admin.hospital)
            args['times'] = times
            return render(request, 'h_admin_homepage/h_admin_homepage.html', args)

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
                                # if event.patient.hospital == request.user.h_admin.hospital:
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
                                    # if event.patient.hospital == request.user.h_admin.hospital:
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
                                    # if event.patient.hospital == request.user.h_admin.hospital:
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
        args['doctors'] = request.user.h_admin.hospital.doctor_set.all()
        args['patients'] = Patient.objects.filter(hospital=request.user.h_admin.hospital)
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
        return render(request, 'h_admin_homepage/h_admin_homepage.html', args)
    return render(request, 'h_admin_homepage/h_admin_homepage.html')


def profile_view(request, pk):
    request.session['dash'] = None
    request.session['emr'] = None
    request.session['profile'] = 1
    request.session['messages'] = None

    template_name = 'h_admin_homepage/profile.html'
    return render(request, template_name)


class UpdateUserInfo(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email', ]
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('h_admin:profile', args=[self.request.user.pk])


class CreateUserFormView(View):
    form_class = UserRegistrationForm
    template_name = 'h_admin_homepage/user_registration_form.html'

    def get(self, request):
        initial = {'email': request.session.get('email', None),
                   'first_name': request.session.get('first_name', None),
                   'last_name': request.session.get('last_name', None),
                   'password': request.session.get('password', None),
                   'usertype': request.session.get('usertype', None)}
        form = self.form_class(None, initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'email': request.session.get('email', None),
                   'first_name': request.session.get('first_name', None),
                   'last_name': request.session.get('last_name', None),
                   'password': request.session.get('password', None),
                   'usertype': request.session.get('usertype', None)}
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            request.session['first_name'] = form.cleaned_data['first_name']
            request.session['last_name'] = form.cleaned_data['last_name']
            request.session['password'] = form.cleaned_data['password1']
            usertype = form.cleaned_data['usertype']
            request.session['usertype'] = usertype
            if usertype == "Doctor":
                return HttpResponseRedirect(reverse('h_admin:register_doctor1'))
            elif usertype == "Nurse":
                return HttpResponseRedirect(reverse('h_admin:register_nurse'))
            else:
                return HttpResponseRedirect(reverse('h_admin:register_admin'))
        return render(request, self.template_name, {'form': form})


class CreateDoctorFormView(View):
    form_class = DoctorRegistrationForm1
    template_name = 'h_admin_homepage/doctor_registration_form1.html'

    def get(self, request):
        initial = {'hospitals': request.session.get('hospitals', None),
                   'max_patients': request.session.get('max_patients', None)}
        form = self.form_class(None, initial=initial)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        initial = {'hospitals': request.session.get('hospitals', None),
                   'max_patients': request.session.get('max_patients', None)}
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            hospitals = form.cleaned_data['hospitals']
            hospital_list = []
            for hospital in hospitals:
                hospital_list.append(hospital.pk)
            request.session['max_patients'] = form.cleaned_data['max_patients']
            request.session['hospital_list'] = hospital_list
            return HttpResponseRedirect(reverse('h_admin:register_doctor2'))
        return render(request, self.template_name, {'form': form})


class CreateDoctor2FormView(View):
    form_class = DoctorRegistrationForm2
    template_name = 'h_admin_homepage/doctor_registration_form2.html'

    def get(self, request):
        form = self.form_class(hospital_list=request.session['hospital_list'])
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'nurses': request.session.get('nurses', None)}
        form = self.form_class(request.POST, initial=initial, hospital_list=request.session['hospital_list'])
        if form.is_valid():
            user = User.objects.create_user(email=request.session['email'],
                                            first_name=request.session['first_name'],
                                            last_name=request.session['last_name'],
                                            password=request.session['password'],
                                            is_staff=True)
            hospitals = []
            nurses = form.cleaned_data['nurses']
            for hospital in request.session['hospital_list']:
                hospitals.append(Hospital.objects.get(pk=hospital))

            doctor = Doctor.objects.create(max_patients=request.session['max_patients'])
            doctor.user = user
            doctor.hospitals = request.session['hospital_list']
            doctor.nurses = form.cleaned_data['nurses']
            doctor.save()
            desc = 'Hospital Admin '+request.user.get_full_name() + ' registered new Doctor ' + \
                   doctor.user.get_full_name()
            log = Log.objects.create(
                type='create',
                date_time=timezone.now(),
                actor=request.user,
                subject=user,
                hospital=request.user.h_admin.hospital,
                description=desc
            )

            return HttpResponseRedirect(reverse('h_admin:index'))
        return render(request, self.template_name, {'form': form})


class CreateNurseFormView(View):
    form_class = NurseRegistrationForm
    template_name = 'h_admin_homepage/nurse_registration_form.html'

    def get(self, request):
        initial = {'hospital': request.session.get('hospital', None)}
        form = self.form_class(None, initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'hospital': request.session.get('hospital', None)}
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            hospital = form.cleaned_data['hospital'].pk
            request.session['hospital'] = hospital
            return HttpResponseRedirect(reverse('h_admin:register_nurse2'))
        return render(request, self.template_name, {'form': form})


class CreateNurse2FormView(View):
    form_class = NurseRegistrationForm2
    template_name = 'h_admin_homepage/nurse_registration_form_2.html'

    def get(self, request):
        form = self.form_class(hospital=request.session['hospital'])
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'doctors': request.session.get('doctors', None)}
        form = self.form_class(request.POST, initial=initial, hospital=request.session['hospital'])
        if form.is_valid():
            user = User.objects.create_user(email=request.session['email'],
                                            first_name=request.session['first_name'],
                                            last_name=request.session['last_name'],
                                            password=request.session['password'],
                                            is_staff=True)
            doctors = form.cleaned_data['doctors']
            hospital = Hospital.objects.get(pk=request.session['hospital'])
            nurse = Nurse.objects.create(user=user, hospital=hospital)
            nurse.doctor_set = doctors

            for doc in doctors:
                doc.save()
            nurse.save()
            user.save()
            desc = 'Hospital Admin ' + request.user.get_full_name() + ' registered new Nurse ' + \
                   nurse.user.get_full_name()
            log = Log.objects.create(
                type='create',
                date_time=timezone.now(),
                actor=request.user,
                subject=user,
                hospital=request.user.h_admin.hospital,
                description=desc
            )
            return HttpResponseRedirect(reverse('h_admin:index'))
        return render(request, self.template_name, {'form': form})


class CreateAdminFormView(View):
    form_class = NurseRegistrationForm
    template_name = 'h_admin_homepage/admin_registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'hospital': request.session.get('hospital', None)}
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            form.save(commit=False)
            user = User.objects.create_user(email=request.session['email'],
                                            first_name=request.session['first_name'],
                                            last_name=request.session['last_name'],
                                            password=request.session['password'],
                                            is_staff=True)
            h_admin = H_Admin.objects.create(user=user,
                                             hospital=form.cleaned_data['hospital'],)
            desc = 'Hospital Admin ' + request.user.get_full_name() + ' registered new Hospital Admin ' + \
                   h_admin.user.get_full_name()

            log = Log.objects.create(
                date_time=timezone.now(),
                type='create',
                actor=request.user,
                subject=user,
                hospital=h_admin.hospital,
                description=desc
            )
            return HttpResponseRedirect(reverse('h_admin:index'))
        return render(request, self.template_name, {'form': form})


class EMRView(ListView):
    template_name = 'h_admin_homepage/emr.html'
    context_object_name = 'patient_list'

    def get_queryset(self):
        self.request.session['dash'] = None
        self.request.session['emr'] = 1
        self.request.session['profile'] = None
        self.request.session['messages'] = None
        return Patient.objects.filter(hospital=self.request.user.h_admin.hospital)


class EMRPatientView(DetailView):
    model = Patient
    template_name = 'h_admin_homepage/patientemr.html'


def viewchronemr(request, pk):
    template_name = 'h_admin_homepage/patient_chronemr.html'
    if request.method == 'GET':
        patient = Patient.objects.get(pk=pk)
        user = User.objects.get(pk=pk)
        log_list = Log.objects.filter(
            Q(subject=user, type='create') |
            Q(subject=user, type='admit') |
            Q(subject=user, type='discharge')
        ).order_by("-date_time")
        return render(request, template_name, {'patient': patient, 'log_list': log_list})


class StatsView(View):
    template_name = 'h_admin_homepage/stats.html'

    def get(self, request):
        admissions = HospitalStay.objects.all()
        reasons = OrderedDict([
            ('Infectious Disease', 0),
            ('Surgery', 0),
            ('Poisoning/Drugs', 0),
            ('Traumatic Injury', 0),
            ('Cardiac Issues', 0),
            ('Chronic Illness', 0),
            ('Other', 0)
        ])
        for key in reasons:
            for admission in admissions:
                if admission.reason == key:
                    reasons[key] += 1

        admitnum = HospitalStay.objects.count()

        if admitnum != 0:
            for key in reasons:
                reasons[key] = reasons[key]/admitnum
                reasons[key] = round(reasons[key]*100, 2)

        completed_stays = HospitalStay.objects.filter(discharge_date__isnull=False)

        staytimes = OrderedDict([
            ('<1 Day', 0),
            ('1 Day', 0),
            ('2 Days', 0),
            ('3-5 Days', 0),
            ('6-7 Days', 0),
            ('8-10 Days', 0),
            ('11-12 Days', 0),
            ('13-14 Days', 0),
            ('>14 Days', 0),
        ])

        for stay in completed_stays:
            delta = stay.discharge_date - stay.admission_date
            if delta.days == 0:
                staytimes['<1 Day'] += 1
            elif delta.days == 1:
                staytimes['1 Day'] += 1
            elif delta.days == 2:
                staytimes['2 Days'] += 1
            elif delta.days <= 5:
                staytimes['3-5 Days'] += 1
            elif delta.days <= 7:
                staytimes['6-7 Days'] += 1
            elif delta.days <= 10:
                staytimes['8-10 Days'] += 1
            elif delta.days <= 12:
                staytimes['11-12 Days'] += 1
            elif delta.days <= 14:
                staytimes['13-14 Days'] += 1
            else:
                staytimes['>14 Days'] += 1

        staynums = completed_stays.count()

        if staynums != 0:
            for key in staytimes:
                staytimes[key] = staytimes[key] / staynums
                staytimes[key] = round(staytimes[key] * 100, 2)

        prescriptions = Prescription.objects.all()
        prescnum = prescriptions.count()

        drugs = OrderedDict((presc.name,0) for presc in prescriptions)

        for presc in prescriptions:
            drugs[presc.name] += 1

        for drug in drugs:
            drugs[drug] = drugs[drug] / prescnum
            drugs[drug] = round(drugs[drug] * 100, 2)

        log_list = Log.objects.all().filter(hospital=request.user.h_admin.hospital).order_by('-date_time')
        return render(request, self.template_name, {'log_list': log_list, 'reason_percentages': reasons, 'stay_percentages': staytimes, 'drugs': drugs})


class UploadCsvFile(View):
    template_name = 'h_admin_homepage/upload_csv_form.html'

    def get(self, request):
        form = UploadFileForm()
        return render(request, 'h_admin_homepage/upload_csv_form.html', {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file'].file
            myfile = TextIOWrapper(file, encoding='ASCII', errors='replace')
            load_csv(file=myfile)
        else:
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect(reverse('h_admin:index'))


class DeleteEvent(DeleteView):
    model = Event

    def get_success_url(self):
        return reverse_lazy('h_admin:index')

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
            hospital=request.user.h_admin.hospital,
            type='delete',
            description=('Hospital Administrator '+request.user.get_full_name() +
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