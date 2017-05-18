from django.test import TestCase

from h_admin_homepage.forms import *
from accounts.models import *


class TestDoctorRegistrationForms(TestCase):

    def setUp(self):
        hospital = Hospital.objects.create(name='Hospital', address='Address')

    def test_max_patients_form_valid(self):
        form = DoctorRegistrationForm1(data={'max_patients': 5})

        self.assertTrue(form.is_valid())

    def test_max_patients_form_invalid(self):
        form = DoctorRegistrationForm1(data={'max_patients': -10})

        self.assertFalse(form.is_valid())
