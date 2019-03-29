from datetime import timedelta

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from .models import Flight


class FlightSerializer(ModelSerializer):
    """Flight serializer

    Arguments:
        ModelSerializer {serializer} -- Serializer for flights model
    """
    class Meta:
        model = Flight
        fields = ('__all__')

    def validate_departure_datetime(self, value):
        """
        Check that departure_datetime is not less than 24 hours
        """
        if value < (timezone.now() + timedelta(hours=24)):
            raise ValidationError("Departure_datetime must be at least 24 hours ahead")
        return value

    def validate(self, data):
        """
        Check that departure_datetime is before arrival_datetime.
        """
        if data['departure_datetime'] > data['arrival_datetime']:
            raise ValidationError("Arrival_datetime must occur after departure_datetime")
        return data
