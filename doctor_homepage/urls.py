from django.conf.urls import url
from doctor_homepage import views

app_name = 'doctor'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^event/(?P<pk>[0-9]+)/delete$', views.DeleteEvent.as_view(), name='deleteevent'),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.profile_view, name='profile'),
    url(r'^profile/(?P<pk>[0-9]+)/update/$', views.UpdateUserInfo.as_view(), name='update'),
    url(r'^emr/$', views.EMRView.as_view(), name='emr'),
    url(r'^emr/(?P<pk>[0-9]+)/$', views.EMRPatientView.as_view(), name='patientemr'),
    url(r'^emr/(?P<pk>[0-9]+)/chronological/$', views.viewchronemr, name='chronemr'),

]
