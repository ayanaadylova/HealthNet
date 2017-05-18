from django.conf.urls import url
from . import views

app_name = 'prescription'

urlpatterns = [
    url(r'^addprescription/(?P<pk>[0-9]+)/$', views.CreatePrescriptionView.as_view(), name='add'),
    url(r'^removeprescription/(?P<pk>[0-9]+)/$', views.RemovePrescriptionView.as_view(), name='remove'),
    url(r'^notificationhandler/(?P<pk>[0-9]+)/$', views.PrescriptionNotificationHandler.as_view(), name='notificationhandler'),
]
