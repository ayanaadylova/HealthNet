from django.conf.urls import url
from patient_homepage import views

app_name = 'patient'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^emr/$', views.viewemr, name='emr'),
    url(r'^emr/chronological/$', views.EMRChronView.as_view(), name='chronemr'),
    url(r'^profile/(?P<pk>[0-9]+)/update/$', views.UpdateUserInfo.as_view(), name='update1'),
    url(r'^profile/(?P<pk>[0-9]+)/update2/$', views.UpdatePatientInfo.as_view(), name='update2'),
    url(r'^addextrainfo/$', views.ExtraInfoFormView.as_view(), name='extra'),
    url(r'^event/(?P<pk>[0-9]+)/delete/$', views.DeleteEvent.as_view(), name='deleteevent'),
]