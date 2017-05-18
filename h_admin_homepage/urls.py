from django.conf.urls import url
from h_admin_homepage import views

app_name = 'h_admin'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.profile_view, name='profile'),
    url(r'^profile/(?P<pk>[0-9]+)/update/$', views.UpdateUserInfo.as_view(), name='update'),
    url(r'^register-staff/$', views.CreateUserFormView.as_view(), name='addstaff'),
    url(r'^register-staff/add-doctor-step1/$', views.CreateDoctorFormView.as_view(), name='register_doctor1'),
    url(r'^register-staff/add-doctor-step2/$', views.CreateDoctor2FormView.as_view(), name='register_doctor2'),
    url(r'^register-staff/add-nurse-step1/$', views.CreateNurseFormView.as_view(), name='register_nurse'),
    url(r'^register-staff/add-nurse-step2/$', views.CreateNurse2FormView.as_view(), name='register_nurse2'),
    url(r'^register-staff/add-hospital-admin/$', views.CreateAdminFormView.as_view(), name='register_admin'),
    url(r'^emr/$', views.EMRView.as_view(), name='emr'),
    url(r'^emr/(?P<pk>[0-9]+)/$', views.EMRPatientView.as_view(), name='patientemr'),
    url(r'^emr/(?P<pk>[0-9]+)/chronological/$', views.viewchronemr, name='chronemr'),
    url(r'^statistics/$', views.StatsView.as_view(), name='statistics'),
    url(r'^upload-csv-file/$', views.UploadCsvFile.as_view(), name='upload_csv_file'),
    url(r'^event/(?P<pk>[0-9]+)/delete/$', views.DeleteEvent.as_view(), name='deleteevent'),
]
