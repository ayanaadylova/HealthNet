from django.shortcuts import render
from django.views.generic import View, DetailView, ListView
from .forms import *
from django.http import HttpResponseRedirect
from message.models import Message
from django.utils import timezone


class RemoveMessageView(View):

    def get(self, request, pk):
        msg = Message.objects.get(pk=pk)
        msg.deleted = True
        msg.save()
        return self.post(request, pk)

    def post(self, request, pk):
        return HttpResponseRedirect(reverse('message:inbox'))


class RestoreMessageView(View):

    def get(self, request, pk):
        msg = Message.objects.get(pk=pk)
        msg.deleted = False
        msg.save()
        return self.post(request, pk)

    def post(self, request, pk):
        return HttpResponseRedirect(reverse('message:deleted'))


class InboxView(ListView):
    template_name = 'message/inbox.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        self.request.session['dash'] = None
        self.request.session['emr'] = None
        self.request.session['profile'] = None
        self.request.session['messages'] = 1
        return Message.objects.filter(receiver=self.request.user, deleted=False)


class OutboxView(ListView):
    template_name = 'message/outbox.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


class DeletedView(ListView):
    template_name = 'message/deleted.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user, deleted=True)


class MessageDetailView(DetailView):
    model = Message
    template_name = 'message/detail.html'


class MessageFormView(View):
    form_class = MessageCreationForm
    template_name = 'message/create_message.html'

    def get(self, request):
        query = self.request.GET.get('query')
        if query:
            form = self.form_class(q=query)
        else:
            form = self.form_class(q='none')
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, q='none')
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            priority = form.cleaned_data['priority']
            users = form.cleaned_data['users']
            for u in users:
                m = Message.objects.create(
                    sender=request.user,
                    receiver=u,
                    subject=subject,
                    message=message,
                    priority=priority,
                    time=timezone.now(),
                    deleted=False
                )
            return HttpResponseRedirect(reverse('message:inbox'))
        return render(request, self.template_name, {'form': form})