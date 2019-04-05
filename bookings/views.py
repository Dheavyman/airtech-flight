from uuid import uuid4

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.helpers.validators import validate_resource_exist
from api.helpers.utils import StatusChoices
from .models import Booking
from .serializers import (BookingSerializer,
                          TicketSerializer,
                          TicketStatusSerializer,
                          TicketReservationSerializer,
                          BookingReservationsSerializer)
from .tasks import email_ticket, email_reservation


class BookingListView(APIView):
    """Booking list view

    Arguments:
        APIView {view} -- rest_framework API view
    """
    def post(self, request, format=None):
        booking = request.data
        booking['passenger_id'] = request.user.id
        booking['ticket_number'] = generate_ticket_number()
        serializer = BookingSerializer(data=booking)

        if serializer.is_valid():
            new_booking = serializer.save()
            ticket = TicketSerializer(new_booking)
            email_ticket.delay(ticket.data)

            return Response({
                'status': 'Success',
                'message': 'Ticket booked',
                'data': ticket.data
            },
            status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Error',
            'message': 'Could not book the flight',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        params = request.query_params.copy()
        if params:
            # Check that the query params contain only supported keys
            keys = [key for key in params.keys()]
            invalid_keys = list(
                filter(lambda key: key not in ('ticket', 'flight', 'date', 'status'), keys))
            if invalid_keys:
                return Response({
                    'status': 'Error',
                    'message': f'Invalid query params - {", ".join(invalid_keys)}'
                },
                status=status.HTTP_400_BAD_REQUEST)
            if not 'ticket' in keys and len(keys) == 3:
                # Handle search for bookings based on flight
                # date and status of the flight bookings
                params['status'] = params['status'].title()
                reservations = BookingReservationsSerializer(data=params)
                if not reservations.is_valid():
                    return Response({
                        'status': 'Error',
                        'message': 'Provide valid query parameters',
                        'error': reservations.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST)

                flight_id = params.get('flight')
                flight_status = StatusChoices(params.get('status').title()).name
                date = params.get('date')
                # Handle booked or reserved date based on status passed
                date_condition = {}
                if flight_status == 'R':
                    date_condition['reserved_at__date__lte'] = date
                elif flight_status == 'B':
                    date_condition['created_at__date__lte'] = date
                bookings = Booking.objects.filter(flight_id=flight_id,
                                                  flight_status=flight_status,
                                                  **date_condition)
                serializer = BookingReservationsSerializer(bookings, many=True)

                return Response({
                    'status': 'Success',
                    'message': 'Flight retrieved',
                    'data': {
                        'count': bookings.count(),
                        'reservations': serializer.data
                    }
                },
                status=status.HTTP_200_OK)
            elif 'ticket' in keys and len(keys) == 1:
                # Handle checking of user flight status
                # Users can only check the status of a flight booking they placed
                ticket = TicketStatusSerializer(data=params)

                if not ticket.is_valid():
                    return Response({
                        'status': 'Error',
                        'message': 'Invalid ticket number',
                        'error': ticket.errors
                    },
                    status=status.HTTP_404_NOT_FOUND)

                try:
                    booking = Booking.objects.get(ticket_number=ticket.data['ticket_number'],
                                                  passenger_id=request.user)
                except Booking.DoesNotExist:
                    return Response({
                        'status': 'Error',
                        'message': 'Ticket not found or you don\'t have the permission to view it'
                    },
                    status=status.HTTP_404_NOT_FOUND)

                serializer = TicketSerializer(booking)

                return Response({
                    'status': 'Success',
                    'message': 'Booking retrieved',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK)
            else:
                # Return error message if no valid query params combination is passed
                return Response({
                    'status': 'Error',
                    'message': 'Unsupported query params combination'
                },
                status=status.HTTP_400_BAD_REQUEST)


class BookingDetailView(APIView):
    """Booking detail view

    Arguments:
        APIView {view} -- rest_framework API view
    """
    @validate_resource_exist(Booking, 'booking')
    def put(self, request, booking_pk, format=None, **kwargs):
        instance = kwargs['booking']
        if instance.flight_status == 'R':
            return Response({
                'status': 'Error',
                'message': 'Flight already reserved'
            },
            status=status.HTTP_409_CONFLICT)

        request.data['flight_status'] = 'R'
        request.data['reserved_at'] = timezone.now()
        serializer = TicketReservationSerializer(instance, data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            ticket = TicketSerializer(instance)
            email_reservation.delay(ticket.data)

            return Response({
                'status': 'Success',
                'message': 'Flight reserved',
                'data': ticket.data
            },
            status=status.HTTP_200_OK)

        return Response({
            'status': 'Error',
            'message': 'Flight not reserved',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

def generate_ticket_number():
    while True:
        unique_str = str(uuid4())[:6].upper()
        if not Booking.objects.filter(ticket_number=unique_str).exists():
            break
    return unique_str
