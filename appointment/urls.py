from django.conf.urls import url
from . import views
app_name = 'appointment'

urlpatterns = [
    url(r'^event/(?P<pk>[0-9]+)/update/$', views.UpdateEventDate.as_view(), name='updateevent'),
    url(r'^event/(?P<pk>[0-9]+)/update2/$', views.UpdateEventTime.as_view(), name='updateevent2'),
    url(r'^event/(?P<pk>[0-9]+)/update3/$', views.UpdateEventEndTime.as_view(), name='updateevent3'),
    url(r'^event/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name='eventdetail'),
    url(r'^eventnotification/(?P<pk>[0-9]+)/$', views.EventNotificationHandler.as_view(), name='eventnotificationhandler'),
    url(r'^makeappointment/step0/$', views.MakeAppointmentChooseDoctor.as_view(), name='makeappointmentchoosedoctor'),
    url(r'^makeappointment/step1/$', views.MakeAppointmentDate.as_view(), name='makeappointmentdate'),
    url(r'^makeappointment/step1/doctor/$', views.MakeAppointmentDateDoctor.as_view(), name='doctormakeappointmentdate'),
    url(r'^makeappointment/step2/$', views.MakeAppointmentTime.as_view(), name='makeappointmenttime'),
    url(r'^makeappointment/step3/$', views.MakeAppointmentEndTime.as_view(), name='makeappointmentendtime'),
    url(r'^calendarappointment/$', views.MakeCalendarAppointment.as_view(), name='calendarappointment'),
]
