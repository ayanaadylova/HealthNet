from django import forms
from django.db.models import Q
from accounts.models import *
from django.forms import Form


class MessageCreationForm(Form):
    users = forms.ModelMultipleChoiceField(queryset=[])

    def __init__(self, *args, **kwargs):
        q = kwargs.pop('q')
        super(MessageCreationForm, self).__init__(*args, **kwargs)

        if q == 'none':
            user_set = User.objects.filter(is_superuser=False, is_staff=True)
        elif " " in q:
            loc = q.find(" ")
            half1 = q[:loc]
            half2 = q[(loc+1):]
            user_set = User.objects.filter(
                Q(first_name__contains=half1) |
                Q(last_name__contains=half1) |
                Q(email__contains=half1) |
                Q(first_name__contains=half2) |
                Q(last_name__contains=half2) |
                Q(email__contains=half2)
            )
        else:
            user_set = User.objects.filter(
                Q(first_name__contains=q) |
                Q(last_name__contains=q) |
                Q(email__contains=q)
            )
        if user_set is not None:
            self.fields['users'] = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple,
                                                                  queryset=user_set,
                                                                  required=True)
        else:
            msg = "There are no staff members with '" + q + "' in their name or email. Try again."
            self.add_error('users', msg)
        self.fields['priority'] = forms.ChoiceField(choices=(
                                                        ('3', 'Low'),
                                                        ('2', 'Medium'),
                                                        ('1', 'High')
                                                    ))
        self.fields['subject'] = forms.CharField(max_length=32)
        self.fields['message'] = forms.CharField(widget=forms.Textarea, max_length=256)




