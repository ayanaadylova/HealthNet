from django.test import TestCase
from prescription.forms import *


class PrescriptionFormTest(TestCase):
    def testPrescriptionform_valid(self):
        form = CreatePrescriptionForm(data= {'name': 'Vicodin',
                                             'information': 'blahblahblah',
                                             'start_date': datetime.date(5,5,2020),
                                             'end_date': datetime.date(5,6,2020)})

        self.assertTrue(form.is_valid())

    def testPrescriptionForm_swappeddates(self):
        form = CreatePrescriptionForm(data= {'name': 'Vicodin',
                                             'information': 'blahblahblah',
                                             'start_date': datetime.date(5,6,2020),
                                             'end_date': datetime.date(5,5,2020)})

        self.assertFalse(form.is_valid())
