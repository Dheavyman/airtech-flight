from rest_framework.serializers import ModelSerializer, CharField, ValidationError
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


class TicketStatusSerializer(ModelSerializer):
    """Ticket status serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    ticket = CharField(write_only=True, source='ticket_number')
    ticket_number = CharField(read_only=True)

    class Meta:
        model = Booking
        fields = ('ticket_number', 'ticket')


class TicketReservationSerializer(ModelSerializer):
    """Ticket reservation serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    class Meta:
        model = Booking
        fields = ('flight_status', 'amount_paid', 'reserved_at')

    def validate(self, data):
        if not 'amount_paid' in data:
            raise ValidationError('Field amount paid is required')
        if data['amount_paid'] != self.instance.flight_id.flight_cost.amount:
            raise ValidationError('Amount paid is not equal to the flight cost')
        return data
