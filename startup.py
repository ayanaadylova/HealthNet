from healthnet import views
from test_result.models import TestResult
from django.utils import timezone
from log.models import *
import os

views.load_csv(file=open(os.path.join('', 'initial.csv')))

# The following creates some test results/hospital stays for the R2 demonstration
patient = (User.objects.get(email="patient1@gmail.com")).patient
patient.isInHospital = True
tr = TestResult.objects.create(name="Cancer Screening",
                          date=timezone.now().date(),
                          information="Patient was screened for lung cancer. There are no pressing signs of disease.",
                          patient=patient,
                          file="",
                          is_released=True)

log1 = Log.objects.create(date_time=timezone.now(),
                          actor=patient.doctor.user,
                          subject=patient.user,
                          description=tr.information,
                          type='create',
                          hospital=patient.hospital)
TestResultLog.objects.create(log=log1,
                             date=tr.date,
                             name=tr.name,
                             information=tr.information,
                             is_released=True)

hs = HospitalStay.objects.create(patient = patient,
                            hospital = patient.hospital,
                            admission_date = timezone.now().date(),
                            reason = "Traumatic Injury",
                            admission_details = "Patient is believed to have a broken hip, will need to stay a few days.",
                            admit_employee = User.objects.get(email="doctor1@gmail.com"),
                            discharge_employee = User.objects.get(email="doctor1@gmail.com"))
patient.save()
log2 = Log.objects.create(date_time=timezone.now(),
                          actor=patient.doctor.user,
                          subject=patient.user,
                          description=hs.admission_details,
                          type='admit',
                          hospital=patient.hospital)
AdmissionLog.objects.create(log=log2, reason=hs.reason)
