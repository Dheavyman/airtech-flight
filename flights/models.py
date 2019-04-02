from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from djmoney.models.fields import MoneyField


class Flight(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]+$', 'Must be only alphanumeric characters')

    flight_number = models.CharField(max_length=20, validators=[alphanumeric])
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    flight_cost = MoneyField(max_digits=19, decimal_places=2, default_currency='USD')
    departing = models.CharField(max_length=32)
    departing_airport = models.CharField(max_length=3)
    destination = models.CharField(max_length=32)
    destination_airport = models.CharField(max_length=3)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
