from django.shortcuts import render
from .forms import *
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
import os.path
from django.utils import timezone
from django.conf import settings
from log.models import *


class CreateTestResultView(View):
    form_class = CreateTestResultForm
    template_name = 'test_result/create_test_result_form.html'

    def get(self, request, pk):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'pk': pk})

    def post(self, request, pk):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            testresult = TestResult.objects.create(
                name=form.cleaned_data['name'],
                information=form.cleaned_data['information'],
                date=form.cleaned_data['date'],
                patient=Patient.objects.get(pk=pk),
                file=form.cleaned_data['file'],
                is_released=not form.cleaned_data['is_released'],
            )
            subject = User.objects.get(pk=pk)
            log = Log.objects.create(
                date_time=timezone.now(),
                actor=request.user,
                subject=subject,
                description="Test result for " + subject.get_full_name() + " added by " + request.user.get_full_name(),
                type='create',
                hospital=subject.patient.hospital
            )
            TestResultLog.objects.create(
                log=log,
                date=testresult.date,
                name=testresult.name,
                information=testresult.information,
                file=testresult.file,
                is_released=testresult.is_released
            )
            if not testresult.is_released:
                notification = Notification.objects.create(
                    name="Test result needs approval: " + testresult.name,
                    recipient=testresult.patient.doctor.user,
                )
                ApproveTestResultNotification.objects.create(notification=notification, test_result=testresult.pk)
            else:
                notification = Notification.objects.create(
                    name="Test result is released: " + testresult.name,
                    recipient=testresult.patient.user,
                )
                TestResultNotification.objects.create(notification=notification)
            if H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:patientemr', args=[pk]))
            elif Doctor.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('doctor:patientemr', args=[pk]))
            elif Nurse.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('nurse:patientemr', args=[pk]))
        return render(request, self.template_name, {'form': form, 'pk': pk})


class FileView(View):
    template_name = 'test_result/test_result_file.html'

    def get(self, request, pk):
        test_result = TestResult.objects.get(pk=pk)
        filename = os.path.join(settings.MEDIA_ROOT, test_result.file.name)
        extension = test_result.file.name.split('.')[-1]
        if extension == 'pdf':
            with open(filename, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'filename=test_result_file.pdf'
                return response
        elif extension == 'png' or extension == 'jpeg' or extension == 'jpg':
            with open(filename, 'rb') as image:
                response = HttpResponse(image.read(), content_type='image/png')
                return response


class LogFileView(View):
    template_name = 'test_result/test_result_file.html'

    def get(self, request, pk):
        log = TestResultLog.objects.get(pk=pk)
        test_result = TestResult.objects.get(name=log.name)
        filename = os.path.join(settings.MEDIA_ROOT, test_result.file.name)
        extension = test_result.file.name.split('.')[-1]
        if extension == 'pdf':
            with open(filename, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'filename=test_result_file.pdf'
                return response
        elif extension == 'png' or extension == 'jpeg':
            with open(filename, 'rb') as image:
                response = HttpResponse(image.read(), content_type='image/png')
                return response


class TestResultNotificationHandler(View):

    def get(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        try:
            return HttpResponseRedirect(reverse_lazy('patient:emr'))
        finally:
            notification.delete()


class ApproveTestResultNotificationHandler(View):
    template_name = 'test_result/approve_test_result.html'
    form_class = TestResultForm

    def get(self, request, pk):
        form = self.form_class()
        notification = Notification.objects.get(pk=pk)
        testresult = TestResult.objects.get(pk=notification.approvetestresultnotification.test_result)
        return render(request, self.template_name, {'testresult': testresult})

    def post(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        testresult = TestResult.objects.get(pk=notification.approvetestresultnotification.test_result)
        testresult.is_released = True
        testresult.save()
        newnotification = Notification.objects.create(
            name="Test result is released: " + testresult.name,
            recipient=testresult.patient.user,
        )
        TestResultNotification.objects.create(notification=newnotification)
        notification.delete()
        return HttpResponseRedirect(reverse('doctor:patientemr', args=[testresult.patient.pk]))


class CancelApproveTestResultNotificationHandler(View):

    def get(self, request, pk):
        patient = TestResult.objects.get(pk=pk).patient.pk
        if ApproveTestResultNotification.objects.filter(test_result=pk).exists():
            if Doctor.objects.filter(pk=request.user.pk).exists():
                notification = ApproveTestResultNotification.objects.get(test_result=pk).notification
                try:
                    return HttpResponseRedirect(reverse('doctor:patientemr', args=[patient]))
                finally:
                    notification.delete()
            elif H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:patientemr', args=[patient]))
        else:
            if Doctor.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('doctor:patientemr', args=[patient]))
            elif H_Admin.objects.filter(pk=request.user.pk).exists():
                return HttpResponseRedirect(reverse('h_admin:patientemr', args=[patient]))


class ApproveTestResult(View):
    template_name = 'test_result/approve_test_result.html'
    form_class = TestResultForm

    def get(self, request, pk):
        form = self.form_class()
        testresult = TestResult.objects.get(pk=pk)
        if Doctor.objects.filter(pk=request.user.pk).exists():
            if ApproveTestResultNotification.objects.filter(test_result=pk).exists():
                notification = ApproveTestResultNotification.objects.get(test_result=pk).notification
                notification.delete()
        return render(request, self.template_name, {'testresult': testresult})

    def post(self, request, pk):
        if H_Admin.objects.filter(pk=request.user.pk).exists():
            if ApproveTestResultNotification.objects.filter(test_result=pk).exists():
                notification = ApproveTestResultNotification.objects.get(test_result=pk).notification
                notification.delete()
        testresult = TestResult.objects.get(pk=pk)
        patient = testresult.patient.pk
        testresult.is_released = True
        testresult.save()
        subject = testresult.patient.user
        log = Log.objects.create(
            date_time=timezone.now(),
            actor=request.user,
            subject=subject,
            description="Test result for " + subject.get_full_name() + " released by " + request.user.get_full_name(),
            type='update',
            hospital=subject.patient.hospital
        )
        TestResultLog.objects.create(
            log=log,
            date=testresult.date,
            name=testresult.name,
            information=testresult.information,
            file=testresult.file,
            is_released=testresult.is_released
        )
        newnotification = Notification.objects.create(
            name="Test result is released: " + testresult.name,
            recipient=testresult.patient.user,
        )
        TestResultNotification.objects.create(notification=newnotification)
        if Doctor.objects.filter(pk=request.user.pk).exists():
            return HttpResponseRedirect(reverse('doctor:patientemr', args=[patient]))
        elif H_Admin.objects.filter(pk=request.user.pk).exists():
            return HttpResponseRedirect(reverse('h_admin:patientemr', args=[patient]))