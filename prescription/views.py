from django.shortcuts import render
from .forms import *
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from log.models import *
from django.utils import timezone


class CreatePrescriptionView(View):
    form_class = CreatePrescriptionForm
    template_name = 'prescription/create_prescription_form.html'

    def get(self, request, pk):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'pk': pk})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            refills = form.cleaned_data['refills']
            dosage = form.cleaned_data['dosage']
            prescription = Prescription.objects.create(
                name=form.cleaned_data['name'],
                information=form.cleaned_data['information'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                patient=Patient.objects.get(pk=pk),
                refills=refills,
                dosage=dosage,
                unit=form.cleaned_data['unit'],
            )
            notification = Notification.objects.create(
                name="You have a new prescription assigned: " + prescription.name,
                recipient=prescription.patient.user,
            )
            PrescriptionNotification.objects.create(
                notification=notification,
            )
            log = Log.objects.create(
                date_time=timezone.now(),
                actor=request.user,
                subject=prescription.patient.user,
                hospital=prescription.patient.hospital,
                type='create',
                description='Prescription for ' + prescription.name + ' prescribed to Patient: ' +
                            prescription.patient.user.get_full_name() + ' created by ' + request.user.get_full_name(),
            )
            presclog = PrescLog.objects.create(
                log=log,
                drugname=prescription.name,
                dosage=str(prescription.dosage) + prescription.unit,
                start_date=prescription.start_date,
                end_date=prescription.end_date,
                refills=prescription.refills,
            )
            if H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:patientemr', args=[pk]))
            else:
                return HttpResponseRedirect(reverse('doctor:patientemr', args=[pk]))
        return render(request, self.template_name, {'form': form, 'pk': pk})


class RemovePrescriptionView(View):

    def get(self, request, pk):
        pres = Prescription.objects.get(pk=pk)
        pres.end_date = date.today()
        pres.refills = 0
        pres.information += " --Prescription removed by " + request.user.first_name + " " + request.user.last_name
        pres.removed = True
        pres.save()
        print("prescription pk = " + str(pk))
        notification = Notification.objects.create(
            name="Prescription has been removed: " + pres.name,
            recipient=pres.patient.user,
        )
        RemovedPrescriptionNotification.objects.create(
            notification=notification,
        )
        log = Log.objects.create(
            date_time=timezone.now(),
            actor=request.user,
            subject=pres.patient.user,
            hospital=pres.patient.hospital,
            type='delete',
            description='Prescription for ' + pres.name + ' prescribed to Patient: ' +
                        pres.patient.user.get_full_name() + ' removed by ' + request.user.get_full_name(),
        )
        presclog = PrescLog.objects.create(
            log=log,
            drugname=pres.name,
            dosage=str(pres.dosage) + pres.unit,
            start_date=pres.start_date,
            end_date=pres.end_date,
            refills=pres.refills,
        )
        return self.post(request, pk)

    def post(self, request, pk):
        patientpk = Prescription.objects.get(pk=pk).patient.pk
        if H_Admin.objects.filter(pk=request.user.pk).exists():
            return HttpResponseRedirect(reverse('h_admin:patientemr', args=[patientpk]))
        else:
            return HttpResponseRedirect(reverse('doctor:patientemr', args=[patientpk]))


class PrescriptionNotificationHandler(View):

    def get(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        try:
            return HttpResponseRedirect(reverse_lazy('patient:emr'))
        finally:
            notification.delete()