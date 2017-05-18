from django.test import TestCase
from accounts.models import *
from django.core.urlresolvers import reverse
from django.test import Client
from appointment.models import *


def create_event(name, date, start_time, end_time, doctor, patient):
    return Event.objects.create(name=name,
                                date=date,
                                start_time=start_time,
                                end_time=end_time,
                                patient=patient,
                                doctor=doctor)


def create_doctor():
    user_doctor = User.objects.create_user(email="test_doctor@gmail.com", password="12345pas")
    user_doctor.save()
    doctor = Doctor.objects.create(user=user_doctor, max_patients=10)
    doctor.save()
    return doctor


class CalendarViewTests(TestCase):

    def test_index_view_with_no_events(self):
        """
        If no events exist, just check for default calendar view.
        """
        create_doctor()
        c = Client()
        c.login(email="test_doctor@gmail.com", password="12345pas")
        response = c.get(reverse('doctor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Daily Calendar")

    def test_index_view_with_one_event(self):
        """
        If one event exists, check if it is displayed.
        """
        doctor = create_doctor()
        name = "Appointment"
        date = datetime.date.today()
        start_time = datetime.time(16, 30)
        end_time = datetime.time(17, 00)
        user_patient = User.objects.create_user(email="test_patient@gmail.com", password="12345pas")
        user_patient.save()
        hospital = Hospital.objects.create(name="Hospital", address="Street")
        hospital.save()
        patient = Patient.objects.create(user=user_patient, doctor=doctor, hospital=hospital)
        create_event(name, date, start_time, end_time, doctor=doctor, patient = patient)
        c = Client()
        c.login(email="test_doctor@gmail.com", password="12345pas")
        response = c.get(reverse('doctor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Appointment")


