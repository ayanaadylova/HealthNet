from django.conf.urls import url
from accounts import views

app_name = 'accounts'

urlpatterns = [
    url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.PatientFormView.as_view(), name='register'),
    url(r'^register/step2/$', views.BasicInfo.as_view(), name='register2'),
    url(r'^admitpatient/$', views.AdmissionView.as_view(), name='admit'),
    url(r'^admitpatient/doctor$', views.AdmissionViewDoctor.as_view(), name='admitdoc'),
    url(r'^dischargepatient/$', views.DischargeView.as_view(), name='discharge'),
    url(r'^updatepassword/$', views.PasswordUpdateView.as_view(), name='updatepassword'),
    url(r'^transferpatient/$', views.TransferPatientView.as_view(), name='transfer'),
    url(r'^getdoctors/$', views.AjaxGetDoctorsView.as_view(), name='ajax_get_doctors'),
    url(r'^receivepatient/(?P<pk>[0-9]+)/$', views.ReceivePatientView.as_view(), name='transfernotificationhandler'),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.patient_profile, name='patientprofile'),
    url(r'^updatemedicalinfo/(?P<pk>[0-9]+)/$', views.UpdateMedicalFormView.as_view(), name='updatemedicalinfo'),
    url(r'^help/$', views.HelpView.as_view(), name='help'),
    url(r'^locations/$', views.LocationsView.as_view(), name='locations'),
]
