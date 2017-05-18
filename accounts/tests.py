from django.test import TestCase
from accounts.forms import *
from accounts.models import *
from appointment.forms import *


class PatientRegisterFormTest(TestCase):
    def setUp(self):
        hospital = Hospital.objects.create(name="Hospital", address="Address")
        hospital.save()
        user = User.objects.create(email='docdoc@gmail.com',
                                   first_name='Jacob',
                                   last_name='Walters',
                                   is_staff=True,
                                   date_joined=datetime.date.today(),
                                   is_active=True
                                   )
        user.save()
        doctor = Doctor.objects.create(user=user,
                                       max_patients=5,
                                       )
        doctor.save()

    # tests PatientRegistrationForm with valid data
    def test_PatientRegisterForm_valid(self):
        form = PatientRegistrationForm(data={'first_name': "Test", 'last_name': "Patient", 'email': "test@gmail.com",
                                             'password1': "pass1234", 'password2': "pass1234",
                                             'hospital': Hospital.objects.get(name="Hospital")})
        self.assertTrue(form.is_valid())

    # tests PatientRegistrationForm with invalid email
    def test_PatientRegisterForm_invalidEmail(self):
        form = PatientRegistrationForm(data={'first_name': "Test", 'last_name': "Patient", 'email': "@",
                                             'password1': "pass1234", 'password2': "pass1234",
                                             'hospital': Hospital.objects.get(name="Hospital")})
        self.assertFalse(form.is_valid())

    # tests PatientRegistrationForm with non matching passwords
    def test_PatientRegisterForm_invalidPassMatch(self):
        form = PatientRegistrationForm(data={'first_name': "Test", 'last_name': "Patient", 'email': "test@gmail.com",
                                             'password1': "pass1234", 'password2': "pass12345",
                                             'hospital': Hospital.objects.get(name="Hospital")})
        self.assertFalse(form.is_valid())

    # tests PatientRegistrationForm with invalid passwords
    def test_PatientRegisterForm_invalidPassFormat(self):
        form = PatientRegistrationForm(data={'first_name': "Test", 'last_name': "Patient", 'email': "test@gmail.com",
                                             'password1': "pass", 'password2': "pass",
                                             'hospital': Hospital.objects.get(name="Hospital")})
        self.assertFalse(form.is_valid())

    def test_BasicInfoForm_valid(self):
        form = BasicInfoForm(data={'doctor': Doctor.objects.get(max_patients=5),
                                   'date_of_birth': datetime.date(1968, 1, 30),
                                   'insurance_number': "A123456789012"})
        self.assertTrue(form.is_valid())

    def test_basicInfoForm_nodoctor(self):
        form = BasicInfoForm(data={'date_of_birth': datetime.date(1968, 1, 30),
                                   'insurance_number': "A123456789012"})
        self.assertFalse(form.is_valid())

    def test_basicInfoForm_invalidinsurance(self):
        form = BasicInfoForm(data={'doctor': Doctor.objects.get(max_patients=5),
                                   'date_of_birth': datetime.date(1968, 1, 30),
                                   'insurance_number': "123456789012"})
        self.assertFalse(form.is_valid())

    def test_basicInfoForm_invaliddateofbirth(self):
        form = BasicInfoForm(data={'doctor': Doctor.objects.get(max_patients=5),
                                   'date_of_birth': datetime.date(2002, 1, 30),
                                   'insurance_number': "A123456789012"})


class UpdatePasswordTest(TestCase):

    def test_passwordchangeForm_valid(self):
        form = UpdatePasswordTest(data= {'password1': 'pass1234', 'password2': 'pass1234'})

        self.assertTrue(form.is_valid())

    def test_passwordchangeform_blank(self):
        form = UpdatePasswordTest()

        self.assertFalse(form.is_valid())

    def test_passwordchangeform_nonmatch(self):
        form = UpdatePasswordTest(data= {'password1': 'pass1234', 'password2': 'pass12345'})

        self.assertFalse(form.is_valid())

    def test_passwordchangeform_onemissing(self):
        form = UpdatePasswordTest(data= {'password1': '', 'password2': 'pass1234'})

        self.assertFalse(form.is_valid())
