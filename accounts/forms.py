from django import forms
from django.forms import ValidationError
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Patient, User, Hospital, Doctor, HospitalStay
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, Form
import datetime
from django.contrib.auth.password_validation import validate_password
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth import authenticate


class PatientRegistrationForm(UserCreationForm):
    hospital = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        super(PatientRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        all_hospitals = Hospital.objects.all()
        self.fields['hospital'] = forms.ModelChoiceField(queryset=all_hospitals)
        self.fields['password1'].help_text = 'Password must be 8 or more characters, not entirely numbers, and not too common'

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )


class BasicInfoForm(ModelForm):
    today = datetime.date.today()
    date_of_birth = forms.DateField(initial=datetime.date.today(), widget=SelectDateWidget(years=range(1900, today.year+1)))

    def __init__(self, *args, **kwargs):
        hospital_pk = kwargs.pop('hospital')
        super(BasicInfoForm, self).__init__(*args, **kwargs)
        if hospital_pk:
            hospital = Hospital.objects.get(pk=hospital_pk)
            all_doctors = hospital.doctor_set.all()
            available_doctors = []
            for doctor in all_doctors:
                count = 0
                for patient in Patient.objects.filter(doctor=doctor):
                    count += 1
                if count < doctor.max_patients:
                    available_doctors.append(doctor)
            my_queryset = Doctor.objects.filter(pk__in=[o.pk for o in available_doctors])
            self.fields['doctor'] = forms.ModelChoiceField(queryset=my_queryset)

    def clean_insurance_number(self):
        inum = self.cleaned_data['insurance_number']
        errors = []
        if inum is None:
            errors.append(ValidationError(_('This field is required'), code='missing'))
        if not len(inum) == 13:
            errors.append(ValidationError(_('Insurance number must be 13 characters long'), code='invalid_length'))
        if not inum[0].isupper():
            errors.append(ValidationError(_('The first character must be a capital letter'), code='invalid_char'))
        if len(errors) == 0:
            return inum
        else:
            raise ValidationError(errors)

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = datetime.date.today()
        if today == dob:
            raise ValidationError(_('Change this field to be your date of birth'))
        elif not today - dob >= datetime.timedelta(days=6570):
            raise ValidationError(_('You are not old enough to register, you must be at least 18 years old'))
        return dob

    class Meta:
        model = Patient
        fields = (
            'doctor',
            'date_of_birth',
            'insurance_number',
        )
        help_texts = {
            'insurance_number': _('13 characters, first must be a capital letter'),
        }


class ExtraInfoForm(Form):

    def __init__(self, *args, **kwargs):
        super(ExtraInfoForm, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.CharField(label="Your Address")
        self.fields['phone_number'] = forms.RegexField(regex=r'^\+?1?\d{9,15}$', label="Your phone number", error_message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                                       help_text="Phone number should have the following format: '+999999999'. Up to 15 digits allowed.")
        self.fields['emergency_first_name'] = forms.CharField(label="Emergency contact first name")
        self.fields['emergency_last_name'] = forms.CharField(label="Emergency contact last name")
        self.fields['emergency_phone_number'] = forms.RegexField(regex=r'^\+?1?\d{9,15}$', label="Emergency contact phone number", error_message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        self.fields['emergency_address'] = forms.CharField(label="Emergency contact address")
        self.fields['emergency_relationship'] = forms.ChoiceField(label="Relationship",
                                                                help_text="How emergency contact is related to you",
                                                                choices=(('Parent/Guardian', 'Parent/Guardian'),
                                                                         ('Spouse', 'Spouse'),
                                                                         ('Friend', 'Friend'),
                                                                         ('Sibling', 'Sibling'),
                                                                         ('Other', 'Other')))


class UpdateBasicMedicalInfoForm(Form):

    def __init__(self, *args, **kwargs):
        super(UpdateBasicMedicalInfoForm, self).__init__(*args, **kwargs)
        self.fields['height_ft'] = forms.IntegerField(label="Feet", help_text="Enter height")
        self.fields['height_in'] = forms.IntegerField(label="Inches", help_text="Enter height to the nearest inch")
        self.fields['weight'] = forms.IntegerField(help_text="Enter weight in pounds")
        self.fields['blood_type'] = forms.ChoiceField(choices=(
                                                      ('A+', 'A+'), ('A-', 'A-'),
                                                      ('B+', 'B+'), ('B-', 'B-'),
                                                      ('AB+', 'AB+'), ('AB-', 'AB-'),
                                                      ('O+', 'O+'), ('O-', 'O-'),
                                                      ))

    def clean_height_ft(self):
        ft = self.cleaned_data['height_ft']
        if ft < 1 or ft > 10:
            raise ValidationError(_('Invalid number of feet. Enter a value between 1 and 10'))
        return ft

    def clean_height_in(self):
        inch = self.cleaned_data['height_in']
        if inch < 0 or inch > 11:
            raise ValidationError(_('Invalid number of inches. Enter a value between 0 and 11'))
        return inch

    def clean_weight(self):
        wt = self.cleaned_data['weight']
        if wt < 1 or wt > 1500:
            raise ValidationError(_('Invalid weight. Enter a value between 1 and 1500'))
        return wt


class LoginForm(Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            self.add_error('password', ValidationError(_('Invalid email or password. Try again')))
        return self.cleaned_data


class AdmissionForm(ModelForm):
    patient = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        self.fields['patient'].required = True
        self.fields['reason'].required = True
        available_patients = Patient.objects.filter(isInHospital=False)
        self.fields['patient'] = forms.ModelChoiceField(queryset=available_patients)
        self.fields['admission_details'] = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = HospitalStay
        fields = (
            'patient',
            'reason',
            'admission_details',
        )


class AdmissionFormDoctor(ModelForm):
    patient = forms.ModelChoiceField(queryset=[])
    hospital = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AdmissionFormDoctor, self).__init__(*args, **kwargs)
        self.fields['patient'].required = True
        self.fields['hospital'].required = True
        self.fields['reason'].required = True
        available_patients = Patient.objects.filter(isInHospital=False)
        self.fields['patient'] = forms.ModelChoiceField(queryset=available_patients)
        h_list = []
        for h in user.doctor.get_hospitals():
            h_list.append(h.pk)
        all_hospitals = Hospital.objects.filter(pk__in=h_list)
        self.fields['hospital'] = forms.ModelChoiceField(queryset=all_hospitals)
        self.fields['admission_details'] = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = HospitalStay
        fields = (
            'patient',
            'hospital',
            'reason',
            'admission_details',
        )


class DischargeForm(ModelForm):
    patient = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DischargeForm, self).__init__(*args, **kwargs)

        if hasattr(user,'doctor'):
            available_patients = Patient.objects.filter(doctor=user.doctor, isInHospital=True)
        else:
            available_patients = Patient.objects.filter(hospital=user.h_admin.hospital, isInHospital=True)

        self.fields['patient'] = forms.ModelChoiceField(queryset=available_patients)
        self.fields['patient'].required = True
        self.fields['discharge_details'] = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = HospitalStay
        fields = (
            'patient',
            'discharge_details',
        )


class PasswordUpdateForm(Form):

    def __init__(self, *args, **kwargs):
        super(PasswordUpdateForm, self).__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(widget=forms.PasswordInput, label='Password', required=True)
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput, label='Password confirmation', required=True)

    def clean_password1(self):
        try:
            p1 = self.cleaned_data['password1']
        except KeyError:
            raise ValidationError(_('This field is required'))
        if validate_password(p1) is None:
            return p1

    def clean_password2(self):
        try:
            p2 = self.cleaned_data['password2']
        except KeyError:
            raise ValidationError(_('This field is required'))

        if validate_password(p2) is None:
            return p2

    def clean(self):
        data = super(PasswordUpdateForm, self).clean()
        p1 = self.clean_password1()
        p2 = self.clean_password2()
        if not p1 == p2:
            self.add_error('password2', ValidationError(_('Password and confirmation must match. Try again.')))
        return data


class TransferPatientForm(Form):
    patient = forms.ModelChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TransferPatientForm, self).__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'doctor'):
                # Doctor is transferring one of their patients
                self.available_patients = Patient.objects.filter(doctor=user.doctor, isInTransit=False)
            elif hasattr(user, 'h_admin'):
                # H_admin or a Nurse
                self.available_patients = Patient.objects.filter(hospital=user.h_admin.hospital, isInTransit=False)
            else:
                # Nurse
                self.available_patients = Patient.objects.filter(hospital=user.nurse.hospital, isInTransit=False)
            self.fields['patient'] = forms.ModelChoiceField(queryset=self.available_patients)
            all_hospitals = Hospital.objects.all()
            all_doctors = Doctor.objects.all()
            self.fields['patient'].required = True
            self.fields['hospital'] = forms.ModelChoiceField(queryset=all_hospitals)
            self.fields['hospital'].required = True
            self.fields['doctor'] = forms.ModelChoiceField(queryset=all_doctors)
            self.fields['doctor'].required = True

    class Meta:
        fields = (
            'patient'
            'hospital'
            'doctor'
        )
