from django.shortcuts import render
from django.contrib.auth import logout
from django.utils import timezone
from log.models import *
from prescription.models import Prescription
from appointment.models import Event
import datetime
import csv


def homepage_redirect(request):
    logout(request)
    return render(request, 'accounts/homepage.html')


def load_csv(file):

    reader = csv.reader(file)
    patients = []
    doctors = []
    nurses = []
    admins = []
    prescs = []
    events = []
    for row in reader:
        if row[0] == 'Patient':
            patients.append([])
            for i in row:
                patients[len(patients) - 1].append(i)
        elif row[0] == 'Doctor':
            doctors.append([])
            for i in row:
                doctors[len(doctors) - 1].append(i)
        elif row[0] == 'Hospital Admin':
            admins.append([])
            for i in row:
                admins[len(admins) - 1].append(i)
        elif row[0] == 'Nurse':
            nurses.append([])
            for i in row:
                nurses[len(nurses) - 1].append(i)
        elif row[0] == 'Prescription':
            prescs.append([])
            for i in row:
                prescs[len(prescs) - 1].append(i)
        elif row[0] == 'Event':
            events.append([])
            for i in row:
                events[len(events) - 1].append(i)
        elif row[0] == 'Hospital':
            Hospital.objects.create(name=row[1],
                                    address=row[2],
                                    phone_number=row[3])
        elif row[0] == 'Prescription':
            prescs.append(row)
        elif row[0] == 'Event':
            events.append(row)
    for n in nurses:
        newuser = User.objects.create(email=n[1],
                                      first_name=n[2],
                                      last_name=n[3],
                                      is_active=bool(n[7]))
        newuser.set_password(n[4])
        newuser.is_staff = True
        newuser.save()
        hospital = Hospital.objects.get(name=n[5])
        Nurse.objects.create(user=newuser,
                             hospital=hospital)
    for a in admins:
        newuser = User.objects.create(email=a[1],
                                      first_name=a[2],
                                      last_name=a[3],
                                      is_active=bool(a[6]))
        newuser.set_password(a[4])
        newuser.is_staff = True
        newuser.save()
        hospital = Hospital.objects.get(name=a[5])
        H_Admin.objects.create(user=newuser,
                               hospital=hospital)
    for d in doctors:
        newuser = User.objects.create(email=d[1],
                                      first_name=d[2],
                                      last_name=d[3],
                                      is_active=bool(d[8]))
        newuser.set_password(d[4])
        newuser.is_staff = True
        newuser.save()
        newdoctor = Doctor.objects.create(user=newuser,
                                          max_patients=d[6])
        for hospital in d[5].split(';'):
            h = hospital.strip()
            myhospital = Hospital.objects.get(name=h)
            newdoctor.hospitals.add(myhospital)
        for nurse in d[7].split(';'):
            nurse_user = User.objects.get(email=nurse.strip())
            nurse = nurse_user.nurse
            newdoctor.nurses.add(nurse)
        newdoctor.save()
    for p in patients:
        newuser = User.objects.create(email=p[1],
                                      first_name=p[2],
                                      last_name=p[3],
                                      is_active=bool(p[9]))
        newuser.set_password(p[4])
        newuser.save()
        hospital = Hospital.objects.get(name=p[5])
        doctor_user = User.objects.get(email=p[6])
        doctor = doctor_user.doctor
        date = datetime.datetime.strptime(p[8], "%m/%d/%Y").date()
        Patient.objects.create(user=newuser,
                               hospital=hospital,
                               doctor=doctor,
                               insurance_number=p[7],
                               date_of_birth=date)
    for p in prescs:

        patient_user = User.objects.get(email=p[7])
        patient = patient_user.patient
        start_date = datetime.datetime.strptime(p[6], "%m/%d/%Y").date()
        end_date = start_date + datetime.timedelta(days=int(p[8]) * int(p[9]))
        dose = p[3]
        unit = None
        c = 1
        dosage = 0
        while unit is None:
            try:
                int(dose[:c])
                c += 1
            except ValueError:
                c -= 1
                unit = dose[c:]
                dosage = int(dose[:c])

        prescription = Prescription.objects.create(name=p[1],
                                    information=p[2],
                                    unit=unit,
                                    dosage=dosage,
                                    patient=patient,
                                    refills=p[8],
                                    start_date=start_date,
                                    end_date=end_date)
        log = Log.objects.create(
            date_time=timezone.now(),
            actor=prescription.patient.user,
            subject=prescription.patient.user,
            hospital=prescription.patient.hospital,
            type='create',
            description='Prescription for ' + prescription.name + ' prescribed to Patient: ' +
                        prescription.patient.user.get_full_name() + ' added via csv',
        )
        presclog = PrescLog.objects.create(
            log=log,
            drugname=prescription.name,
            dosage=str(prescription.dosage) + prescription.unit,
            start_date=prescription.start_date,
            end_date=prescription.end_date,
            refills=prescription.refills,
        )
    for e in events:
        doctor_user = User.objects.get(email=e[1])
        doctor = doctor_user.doctor
        if e[2] == '!':
            patient = None
        else:
            patient_user = User.objects.get(email=e[2])
            patient = patient_user.patient
        name = e[3]
        date = datetime.datetime.strptime(e[4], "%m/%d/%Y").date()
        hours = int(e[5][:(e[5].index(':'))])
        minutes = int(e[5][(e[5].index(':')) + 1:])
        start_time = datetime.time(hours, minutes)
        hours = int(e[6][:(e[6].index(':'))])
        minutes = int(e[6][(e[6].index(':')) + 1:])
        end_time = datetime.time(hours, minutes)
        Event.objects.create(doctor=doctor,
                             patient=patient,
                             name=name,
                             date=date,
                             start_time=start_time,
                             end_time=end_time)
