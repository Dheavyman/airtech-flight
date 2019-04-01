from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField

from api.helpers.utils import StatusChoices
from flights.models import Flight


class Booking(models.Model):
    ticket_number = models.CharField(max_length=6, unique=True)
    flight_status = models.CharField(max_length=1,
                                     choices=[(choice.name, choice.value)
                                              for choice in StatusChoices],
                                     default='B')
    created_at = models.DateTimeField(auto_now_add=True)
    reserved_at = models.DateTimeField(null=True)
    amount_paid = MoneyField(max_digits=19, decimal_places=2, default_currency='USD', default=0)
    flight_id = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('flight_id', 'passenger_id')
