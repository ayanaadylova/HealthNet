from django.contrib import admin
from accounts.models import *
from django.contrib.auth.admin import UserAdmin
from django import forms


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("email",)
    ordering = ("email",)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name',
                       'is_superuser', 'is_staff', 'is_active')}),
        )

    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(Patient)
admin.site.register(Hospital)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(H_Admin)
admin.site.register(Notification)
admin.site.register(AppointmentNotification)
admin.site.register(PrescriptionNotification)
admin.site.register(RemovedPrescriptionNotification)
admin.site.register(TestResultNotification)
admin.site.register(ApproveTestResultNotification)



