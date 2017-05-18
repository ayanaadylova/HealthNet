from django.test import TestCase
from accounts.models import *
from django.core.urlresolvers import reverse
from django.test import Client


def create_nurse():
    user_nurse = User.objects.create_user(email="test_nurse@gmail.com", password="12345pas")
    user_nurse.save()
    hospital = Hospital.objects.create(name="Hospital", address="Street")
    hospital.save()
    nurse = Nurse.objects.create(user=user_nurse, hospital=hospital)
    nurse.save()
    return nurse


class CalendarViewTests(TestCase):

    def test_index_view_with_no_events(self):
        """
        If no events exist, just check for default calendar view.
        """
        create_nurse()
        c = Client()
        c.login(email="test_nurse@gmail.com", password="12345pas")
        response = c.get(reverse('nurse:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Weekly Calendar")

