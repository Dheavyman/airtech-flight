from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Booking
from .serializers import BookingSerializer, TicketSerializer


class BookingListView(APIView):
    """Booking list view

    Arguments:
        APIView {view} -- rest_framework API view
    """
    def post(self, request, format='json'):
        booking = request.data
        booking['passenger_id'] = request.user.id
        serializer = BookingSerializer(data=booking)

        if serializer.is_valid():
            new_booking = serializer.save()
            ticket = TicketSerializer(new_booking)

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
