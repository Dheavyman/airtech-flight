import re

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.helpers.utils import StatusChoices
from users.serializers import UserSerializer
from flights.serializers import FlightSerializer
from .models import Booking

def is_valid_ticket(value):
    if re.search(r"^[a-zA-Z0-9]{6}$", value) is None:
        raise serializers.ValidationError('Ticket number invalid please provide a valid ticket')


class BookingSerializer(serializers.ModelSerializer):
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


class TicketSerializer(serializers.ModelSerializer):
    """Ticket serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    flight_status = serializers.CharField(source='get_flight_status_display')
    passenger = UserSerializer(read_only=True, source='passenger_id')
    flight = FlightSerializer(read_only=True, source='flight_id')

    class Meta:
        model = Booking
        exclude = ('flight_id', 'passenger_id')


class TicketStatusSerializer(serializers.ModelSerializer):
    """Ticket status serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    ticket = serializers.CharField(write_only=True,
                                   source='ticket_number',
                                   validators=[is_valid_ticket])
    ticket_number = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = ('ticket_number', 'ticket')


class TicketReservationSerializer(serializers.ModelSerializer):
    """Ticket reservation serializer

    Arguments:
        ModelSerializer {serializer} -- rest framework model serializer
    """
    class Meta:
        model = Booking
        fields = ('flight_status', 'amount_paid', 'reserved_at')

    def validate(self, data):
        if not 'amount_paid' in data:
            raise serializers.ValidationError('Field amount paid is required')
        if data['amount_paid'] != self.instance.flight_id.flight_cost.amount:
            raise serializers.ValidationError('Amount paid is not equal to the flight cost')
        return data


class BookingReservationsSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True, write_only=True)
    status = serializers.ChoiceField(required=True,
                                     write_only=True,
                                     choices=[(choice.value, choice.name)
                                              for choice in StatusChoices])
    flight_status = serializers.CharField(read_only=True, source='get_flight_status_display')

    class Meta:
        model = Booking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ('date', 'status'):
                self.fields[field].read_only = True

