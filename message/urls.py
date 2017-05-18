from django.conf.urls import url
from . import views

app_name = 'message'

urlpatterns = [
    url(r'^inbox/$', views.InboxView.as_view(), name='inbox'),
    url(r'^outbox/$', views.OutboxView.as_view(), name='outbox'),
    url(r'^deleted/$', views.DeletedView.as_view(), name='deleted'),
    url(r'^new_message/$', views.MessageFormView.as_view(), name='newmessage'),
    url(r'^message/(?P<pk>[0-9]+)/$', views.MessageDetailView.as_view(), name='detail'),
    url(r'^remove/(?P<pk>[0-9]+)/$', views.RemoveMessageView.as_view(), name='remove'),
    url(r'^restore/(?P<pk>[0-9]+)/$', views.RestoreMessageView.as_view(), name='restore'),

]
