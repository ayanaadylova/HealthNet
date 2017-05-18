from django import forms
from django.forms import ModelForm, Form, ValidationError
from .models import *
from django.forms.extras.widgets import SelectDateWidget
from datetime import date
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class CreateTestResultForm(ModelForm):
    date = forms.DateField(widget=SelectDateWidget, initial=date.today())
    information = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Please enter the description'}))
    is_released = forms.BooleanField(required=False, label="Hidden from Patient")

    class Meta:
        model = TestResult
        fields = (
            'name',
            'date',
            'information',
            'file',
            'is_released',
        )

    def clean_file(self):
        if self.cleaned_data['file']:
            content = self.cleaned_data['file']
            content_type = content.content_type.split('/')
            valid_type = False
            for extension in content_type:
                if extension in settings.CONTENT_TYPES:
                    if content._size > settings.MAX_UPLOAD_SIZE:
                        raise ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
                            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
                    else:
                        valid_type = True
            if not valid_type:
                raise ValidationError(_('You must upload a pdf or an image (.png, .jpg, or .jpeg)'))
            return content

        else:
            return None


class TestResultForm(ModelForm):

    class Meta:
        model = TestResult
        fields = (
            'name',
            'date',
            'information',
            'patient',
            'file',
        )