from django import forms
from django.forms import ModelForm
from .models import *
from django.forms.extras.widgets import SelectDateWidget
from datetime import date
import datetime


class CreatePrescriptionForm(ModelForm):
    start_date = forms.DateField(widget=SelectDateWidget, initial=date.today())
    end_date = forms.DateField(widget=SelectDateWidget, initial=(date.today() + datetime.timedelta(days=7)))
    refills = forms.IntegerField(max_value=15, min_value=0)
    dosage = forms.IntegerField(max_value=999, min_value=1)
    information = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Prescription
        fields = (
            'name',
            'information',
            'start_date',
            'end_date',
            'refills',
            'dosage',
            'unit',
        )

