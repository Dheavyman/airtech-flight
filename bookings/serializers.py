from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer
from flights.serializers import FlightSerializer
from .models import Booking


class BookingSerializer(ModelSerializer):
    """Booking serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    class Meta:
        model = Booking
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Booking.objects.all(),
                fields=('flight_id', 'passenger_id'),
                message='Ticket already booked'
            )
        ]


class TicketSerializer(ModelSerializer):
    """Ticket serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    passenger = UserSerializer(read_only=True, source='passenger_id')
    flight = FlightSerializer(read_only=True, source='flight_id')

    class Meta:
        model = Booking
        fields = '__all__'
