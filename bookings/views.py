from uuid import uuid4

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.helpers.validators import validate_resource_exist
from .models import Booking
from .serializers import (BookingSerializer,
                          TicketSerializer,
                          TicketStatusSerializer,
                          TicketReservationSerializer)
from .tasks import email_ticket


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
            'message': 'Could not create the flight',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        ticket = TicketStatusSerializer(data=request.query_params)

        if not ticket.is_valid():
            return Response({
                'status': 'Error',
                'message': 'Provide ticket number in query params as ?ticket=<ticket_number>',
            },
            status=status.HTTP_404_NOT_FOUND)

        try:
            booking = Booking.objects.get(ticket_number=ticket.data['ticket_number'],
                                            passenger_id=request.user)
        except Booking.DoesNotExist:
            return Response({
                'status': 'Error',
                'message': 'Ticket not found'
            },
            status=status.HTTP_404_NOT_FOUND)

        serializer = TicketSerializer(booking)

        return Response({
            'status': 'Success',
            'message': 'Booking retrieved',
            'data': serializer.data
        },
        status=status.HTTP_200_OK)


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
