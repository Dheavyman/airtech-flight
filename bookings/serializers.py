from rest_framework.serializers import ModelSerializer, CharField
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
        extra_kwargs = {'flight_status': {'read_only': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['flight_id'].error_messages[
            'does_not_exist'] = 'Flight with the id "{pk_value}" does not exist'


class TicketSerializer(ModelSerializer):
    """Ticket serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    flight_status = CharField(source='get_flight_status_display')
    passenger = UserSerializer(read_only=True, source='passenger_id')
    flight = FlightSerializer(read_only=True, source='flight_id')

    class Meta:
        model = Booking
        exclude = ('flight_id', 'passenger_id')
