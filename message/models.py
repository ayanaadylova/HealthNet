from django.db import models
from accounts.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    receiver = models.ForeignKey(User, related_name='receiver')
    subject = models.CharField(max_length=32)
    message = models.CharField(max_length=256)
    time = models.DateTimeField()
    choices = (
        ('1', 'High'),
        ('2', 'Medium'),
        ('3', 'Low')
    )
    priority = models.IntegerField(choices=choices)
    deleted = models.BooleanField(default=False)
