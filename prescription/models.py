from django.db import models
from accounts.models import Patient


class Prescription(models.Model):
    name = models.CharField(max_length=100)
    information = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    refills = models.IntegerField()
    dosage = models.IntegerField()
    units = (
        ('g', 'grams'),
        ('mg', 'milligrams'),
        ('mcg', 'micrograms')
    )
    unit = models.CharField(choices=units, max_length=3)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
