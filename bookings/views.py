from uuid import uuid4

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Booking
from .serializers import BookingSerializer, TicketSerializer, TicketStatusSerializer
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

        if ticket.is_valid():
            try:
                booking = Booking.objects.get(ticket_number=ticket.data['ticket_number'],
                                              passenger_id=request.user)
            except Booking.DoesNotExist:
                return Response({
                    'status': 'Error',
                    'message': 'Ticket not found'
                },
                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'status': 'Error',
                'message': 'Provide ticket number in query params as ?ticket=<ticket_number>',
            },
            status=status.HTTP_404_NOT_FOUND)


        serializer = TicketSerializer(booking)

        return Response({
            'status': 'Success',
            'message': 'Booking retrieved',
            'data': serializer.data
        },
        status=status.HTTP_200_OK)

def generate_ticket_number():
    while True:
        unique_str = str(uuid4())[:6].upper()
        if not Booking.objects.filter(ticket_number=unique_str).exists():
            break
    return unique_str
