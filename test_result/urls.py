from django.conf.urls import url
from test_result import views

app_name = 'test_result'

urlpatterns = [
    url(r'^addtestresult/(?P<pk>[0-9]+)/$', views.CreateTestResultView.as_view(), name='add'),
    url(r'^testfile/(?P<pk>[0-9]+)/$', views.FileView.as_view(), name='file'),
    url(r'^testfile/log/(?P<pk>[0-9]+)/$', views.LogFileView.as_view(), name='logfile'),
    url(r'^testresulthandler/(?P<pk>[0-9]+)/$', views.TestResultNotificationHandler.as_view(), name='notificationhandler'),
    url(r'^approvetestresulthandler/(?P<pk>[0-9]+)/$', views.ApproveTestResultNotificationHandler.as_view(), name='approvenotificationhandler'),
    url(r'^cancelapprovetestresult/(?P<pk>[0-9]+)/$', views.CancelApproveTestResultNotificationHandler.as_view(), name='cancelapprovetest'),
    url(r'^approvetestresult/(?P<pk>[0-9]+)/$', views.ApproveTestResult.as_view(), name='approvetestresult'),

]
