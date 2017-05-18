from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.password_validation import password_changed
from django.views.generic import View, ListView
from accounts.forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from log.models import *


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage_redirect'))


class PasswordUpdateView(View):
    form_class = PasswordUpdateForm
    template_name = 'accounts/update_password_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.user
            pw = form.cleaned_data['password2']
            user.set_password(pw)
            password_changed(pw)
            user.save()
            user = authenticate(email=user.email, password=pw)
            login(request, user)
            pk = request.user.pk
            if hasattr(user, 'h_admin'):
                return HttpResponseRedirect(reverse('h_admin:profile', args=[pk]))
            elif hasattr(user, 'patient'):
                return HttpResponseRedirect(reverse('accounts:patientprofile', args=[pk]))
            elif hasattr(user, 'doctor'):
                return HttpResponseRedirect(reverse('doctor:profile', args=[pk]))
            elif hasattr(user, 'nurse'):
                return HttpResponseRedirect(reverse('nurse:profile', args=[pk]))

        return render(request, self.template_name, {'form': form})


class PatientFormView(View):
    form_class = PatientRegistrationForm
    template_name = 'accounts/registration_form1.html'

    def get(self, request):
        initial = {'email': request.session.get('email', None),
                   'first_name': request.session.get('first_name', None),
                   'last_name': request.session.get('last_name', None),
                   'password': request.session.get('password', None),
                   'hospital': request.session.get('hospital', None)}
        form = self.form_class(None, initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        initial = {'email': request.session.get('email', None),
                   'first_name': request.session.get('first_name', None),
                   'last_name': request.session.get('last_name', None),
                   'password': request.session.get('password', None),
                   'hospital': request.session.get('hospital', None)}
        form = self.form_class(request.POST, initial=initial)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            request.session['first_name'] = form.cleaned_data['first_name']
            request.session['last_name'] = form.cleaned_data['last_name']
            request.session['password'] = form.cleaned_data['password1']
            request.session['hospital'] = form.cleaned_data['hospital'].pk
            return HttpResponseRedirect(reverse('accounts:register2'))
        return render(request, self.template_name, {'form': form})


class BasicInfo(View):
    form_class = BasicInfoForm
    template_name = 'accounts/registration_form2.html'

    def get(self, request):
        form = self.form_class(hospital=request.session['hospital'])
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, hospital=request.session['hospital'])
        if form.is_valid():
            form.save(commit=False)
            insurance_number = form.cleaned_data['insurance_number']
            date_of_birth = form.cleaned_data['date_of_birth']
            user = User.objects.create_user(email=request.session['email'],
                                            first_name=request.session['first_name'],
                                            last_name=request.session['last_name'],
                                            password=request.session['password'])
            doctor = form.cleaned_data['doctor']
            hospital = Hospital.objects.get(pk=request.session['hospital'])
            patient = Patient.objects.create(user=user,
                                             doctor=doctor,
                                             hospital=hospital,
                                             date_of_birth=date_of_birth,
                                             insurance_number=insurance_number)
            Log.objects.create(
                date_time=timezone.now(),
                actor=patient.user,
                subject=patient.user,
                hospital=hospital,
                type='create',
                description=(patient.user.first_name+' '+patient.user.last_name+' registered to Hospital: ' +
                             hospital.name)
            )
            user = authenticate(email=user.email, password=request.session['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('patient:index'))
        return render(request, 'accounts/registration_form2.html', {'form': form})


class LoginFormView(View):
    form_class = LoginForm
    template_name = 'accounts/login_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            login(request, user)
            if hasattr(user, 'h_admin'):
                return HttpResponseRedirect(reverse('h_admin:index'))
            elif hasattr(user, 'patient'):
                return HttpResponseRedirect(reverse('patient:index'))
            elif hasattr(user, 'doctor'):
                return HttpResponseRedirect(reverse('doctor:index'))
            elif hasattr(user, 'nurse'):
                return HttpResponseRedirect(reverse('nurse:index'))
        return render(request, self.template_name, {'form': form})


class AdmissionViewDoctor(View):
    form_class = AdmissionFormDoctor
    template_name = 'accounts/admitpatient_doc.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            hospital = form.cleaned_data['hospital']
            today = datetime.date.today()
            reason = form.cleaned_data['reason']
            details = form.cleaned_data['admission_details']
            employee = request.user
            patient.isInHospital = True
            patient.save()
            stay = HospitalStay.objects.create(patient=patient,
                                               hospital=hospital,
                                               admission_date=today,
                                               reason=reason,
                                               admission_details=details,
                                               admit_employee=employee)

            log = Log.objects.create(date_time=timezone.now(),
                                     actor=employee,
                                     subject=patient.user,
                                     description=stay.__str__(),
                                     hospital=hospital,
                                     type='admit')
            AdmissionLog.objects.create(log=log,
                                        reason=reason)

            return HttpResponseRedirect(reverse('doctor:index'))
        return render(request, self.template_name, {'form': form})


class AdmissionView(View):
    form_class = AdmissionForm
    template_name = 'accounts/admitpatient.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            today = datetime.date.today()
            reason = form.cleaned_data['reason']
            details = form.cleaned_data['admission_details']
            employee = request.user
            patient.isInHospital = True
            patient.save()
            if hasattr(employee, 'nurse'):
                hos = request.user.nurse.hospital
            else:
                hos = request.user.h_admin.hospital
            stay = HospitalStay.objects.create(patient=patient,
                                               hospital=hos,
                                               admission_date=today,
                                               reason=reason,
                                               admission_details=details,
                                               admit_employee=employee)

            log = Log.objects.create(date_time=timezone.now(),
                                     actor=employee,
                                     subject=patient.user,
                                     description=stay.__str__(),
                                     hospital=hos,
                                     type='admit')
            AdmissionLog.objects.create(log=log,
                                        reason=reason)
            if hasattr(employee, 'h_admin'):
                return HttpResponseRedirect(reverse('h_admin:index'))
            elif hasattr(employee, 'nurse'):
                return HttpResponseRedirect(reverse('nurse:index'))
        return render(request, self.template_name, {'form': form})


class DischargeView(View):
    form_class = DischargeForm
    template_name = 'accounts/dischargepatient.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            details = form.cleaned_data['discharge_details']
            employee = request.user
            patient.isInHospital = False
            stay = HospitalStay.objects.filter(patient=patient, discharge_date__isnull=True).first()
            hospital = stay.hospital
            stay.discharge_date = datetime.date.today()
            stay.discharge_employee = employee
            stay.discharge_details += details
            patient.save()
            stay.save()

            Log.objects.create(date_time=timezone.now(),
                               actor=employee,
                               subject=patient.user,
                               description=patient.user.first_name + " " + patient.user.last_name + " was discharged from " + hospital.name + ".",
                               hospital=hospital,
                               type='discharge')
            if hasattr(employee, 'h_admin'):
                return HttpResponseRedirect(reverse('h_admin:index'))
            elif hasattr(employee, 'doctor'):
                return HttpResponseRedirect(reverse('doctor:index'))
            elif hasattr(employee, 'nurse'):
                return HttpResponseRedirect(reverse('nurse:index'))
        return render(request, self.template_name, {'form': form})


class UpdateMedicalFormView(View):
    form_class = UpdateBasicMedicalInfoForm
    template_name = 'accounts/medical_form.html'

    def get(self, request, pk):
        patient = Patient.objects.get(pk=pk)
        if patient.height:
            initial = {'height_ft': int(patient.height/12),
                       'height_in': int(patient.height % 12),
                       'weight': patient.weight,
                       'blood_type': patient.blood_type}
            form = self.form_class(None, initial=initial)
        else:
            form = self.form_class()
        return render(request, self.template_name, {'form': form, 'pk': pk})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            height_ft = form.cleaned_data['height_ft']
            height_in = form.cleaned_data['height_in']
            weight = form.cleaned_data['weight']
            blood_type = form.cleaned_data['blood_type']
            patient = Patient.objects.get(pk=pk)
            patient.height = 12*height_ft + height_in
            patient.weight = weight
            patient.blood_type = blood_type
            patient.save()
            if H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:patientemr', args=[pk]))
            elif Doctor.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('doctor:patientemr', args=[pk]))
            else:
                return HttpResponseRedirect(reverse('nurse:patientemr', args=[pk]))
        return render(request, self.template_name, {'form': form, 'pk': pk})


def patient_profile(request, pk):
    if hasattr(request.user, 'patient'):
        request.session['dash'] = None
        request.session['emr'] = None
        request.session['profile'] = 1
        request.session['messages'] = None

    patient = Patient.objects.get(pk=pk)
    template_name = 'accounts/profile.html'
    return render(request, template_name, {'patient': patient})


class TransferPatientView(View):
    form_class = TransferPatientForm
    template_name = 'accounts/transferpatient.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST, user=request.user)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            hospital = form.cleaned_data['hospital']
            doctor = form.cleaned_data['doctor']
            employee = request.user

            log = Log.objects.create(date_time=timezone.now(),
                                     actor=employee,
                                     subject=patient.user,
                                     description=patient.user.first_name + " " + patient.user.last_name + " in transit to " + hospital.name + ".",
                                     hospital=patient.hospital,
                                     type='update'
                                     )
            TransferLog.objects.create(log=log,
                                       destination=hospital,
                                       newdoctor=doctor
                                       )
            transfer = OngoingTransfer.objects.create(patient=patient,
                                                      dest_doctor=doctor,
                                                      dest_hospital=hospital,
                                                      src_doctor=patient.doctor,
                                                      src_hospital=patient.hospital
                                                      )
            notif = Notification.objects.create(name="Patient in Transit to "+hospital.name+".",
                                                recipient=doctor.user)
            ReceiveTransferNotification.objects.create(notification=notif,
                                                       transfer=transfer.pk)
            patient.isInTransit = True
            patient.save()
            if hasattr(employee, 'h_admin'):
                return HttpResponseRedirect(reverse('h_admin:index'))
            elif hasattr(employee, 'doctor'):
                return HttpResponseRedirect(reverse('doctor:index'))
            elif hasattr(employee, 'nurse'):
                return HttpResponseRedirect(reverse('nurse:index'))
        return render(request, self.template_name, {'form': form})


class AjaxGetDoctorsView(View):

    def get(self, request, *args, **kwargs):
        hospital = get_object_or_404(Hospital, pk=request.GET.get('hospital', ''))
        doctor_users = []
        for doc in hospital.doctor_set.iterator():
            count = 0
            for patient in Patient.objects.filter(doctor=doc):
                count += 1
            if count < doc.max_patients:
                doctor_users.append(doc.user)
        return HttpResponse(serializers.serialize('json', doctor_users, fields=('doctor', 'first_name', 'last_name', 'email')), content_type='application/json')


class ReceivePatientView(View):
    template_name = 'accounts/receivepatient.html'

    def get(self, request, pk):
        notif = Notification.objects.get(pk=pk)
        transfer = OngoingTransfer.objects.get(pk=notif.receivetransfernotification.transfer)
        return render(request, self.template_name, {'transfer': transfer})

    def post(self, request, pk):
        employee = request.user
        notif = Notification.objects.get(pk=pk)
        transfer = OngoingTransfer.objects.get(pk=notif.receivetransfernotification.transfer)
        patient = transfer.patient
        log = Log.objects.create(date_time=timezone.now(),
                                 actor=employee,
                                 subject=patient.user,
                                 description=patient.user.first_name + " " + patient.user.last_name + " was received at " + transfer.dest_hospital.name + ".",
                                 hospital=transfer.dest_hospital,
                                 type='update'
                                 )
        TransferLog.objects.create(log=log,
                                   destination=transfer.dest_hospital,
                                   newdoctor=transfer.dest_doctor
                                   )
        patient.doctor = transfer.dest_doctor
        patient.hospital = transfer.dest_hospital
        patient.isInTransit = False
        patient.save()
        notif.delete()
        transfer.delete()
        if hasattr(request.user, 'doctor'):
            return HttpResponseRedirect(reverse('doctor:patientemr', args=[patient.pk]))
        elif hasattr(request.user, 'h_admin'):
            return HttpResponseRedirect(reverse('h_admin:patientemr', args=[patient.pk]))


class HelpView(View):
    template_name = 'accounts/help.html'

    def get(self, request):
        return render(request, self.template_name)


class LocationsView(ListView):
    template_name = 'accounts/locations.html'
    context_object_name = 'hospital_list'

    def get_queryset(self):
        self.request.session['locations'] = 1
        self.request.session['home'] = None
        return Hospital.objects.order_by('name')