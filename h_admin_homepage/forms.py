from django.contrib.auth.forms import UserCreationForm
from accounts.models import User, Doctor, Nurse, Hospital, H_Admin
from django.forms import ModelForm, Form
from django import forms


class UserRegistrationForm(UserCreationForm):

    usertype = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        choices = (
            ('Nurse', 'Nurse'),
            ('Doctor', 'Doctor'),
            ('Admin', 'Hospital Admin')
        )
        self.fields['usertype'] = forms.ChoiceField(choices=choices, required=True, label='Staff Type')

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )


class DoctorRegistrationForm1(ModelForm):
    hospitals = forms.ModelMultipleChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        super(DoctorRegistrationForm1, self).__init__(*args, **kwargs)
        hospital_list = Hospital.objects.all()
        self.fields['hospitals'] = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple,
                                                                  queryset=hospital_list)

    class Meta:
        model = Doctor
        fields = (
            'max_patients',
        )


class DoctorRegistrationForm2(Form):
    nurses = forms.ModelMultipleChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        hospitals = kwargs.pop('hospital_list')
        hospital_list = []
        for h in hospitals:
            hospital_list.append(Hospital.objects.get(pk=h))
        super(DoctorRegistrationForm2, self).__init__(*args, **kwargs)
        nurse_list = Nurse.objects.filter(hospital__in=hospital_list)
        self.fields['nurses'] = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple,
                                                               queryset=nurse_list)


class NurseRegistrationForm(ModelForm):
    hospital = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        super(NurseRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['hospital'] = forms.ModelChoiceField(queryset=Hospital.objects.all())

    class Meta:
        model = Nurse
        fields = (
            'hospital',
        )


class NurseRegistrationForm2(Form):
    doctors = forms.ModelMultipleChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        hospital = Hospital.objects.get(pk=kwargs.pop('hospital'))
        super(NurseRegistrationForm2, self).__init__(*args, **kwargs)
        doctor_list = hospital.doctor_set.all()
        self.fields['doctors'] = forms.ModelMultipleChoiceField(queryset=doctor_list, required=False)


class AdminRegistrationForm(ModelForm):
    hospital = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        super(AdminRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['hospital'] = forms.ModelChoiceField(queryset=Hospital.objects.all())

    class Meta:
        model = H_Admin
        fields = (
            'hospital',
        )


class UploadFileForm(Form):
    file = forms.FileField(required=True)

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        file_type = file.content_type
        if file_type == 'application/octet-stream':
            return file
        if file_type == 'application/vnd.ms-excel':
            return file
        if file_type == 'text/csv':
            return file
        self.add_error('file', 'Please upload a CSV file, your file is type %s' % file_type)


