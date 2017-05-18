from django.db import models
from accounts.models import Patient


class TestResult(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    information = models.CharField(max_length=2500)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    file = models.FileField(blank=True, null=True)
    is_released = models.BooleanField(default=True)

    def __str__(self):
        return self.name
