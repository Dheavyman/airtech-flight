from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, SAFE_METHODS

from .models import Flight
from .serializers import FlightSerializer

def get_flight_or_404(pk):
    try:
        flight = Flight.objects.get(pk=pk)
    except Flight.DoesNotExist:
        return Response({
            'status': 'Error',
            'message': 'Flight not found'
        },
        status=status.HTTP_404_NOT_FOUND)
    return flight


class IsAdminUserOrReadOnly(IsAdminUser):
    """Grant permission to only admin to perform POST, PUT and DELETE requests
    All other authenticated users can perform GET, HEAD and OPTIONS requests

    Arguments:
        IsAdminUser {permission} -- rest_framework IsAdminUser permission
    """
    message = 'Request forbidden, must be an admin'

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


class FlightListView(APIView):
    """Flight list view

    Arguments:
        APIView {view} -- rest_framework API view
    """
    permission_classes = (IsAuthenticated, IsAdminUserOrReadOnly)

    def post(self, request, format='json'):
        flight = request.data
        flight['created_by'] = request.user.id
        serializer = FlightSerializer(data=flight)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'Success',
                'message': 'flight created',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Error',
            'message': 'Could not create the flight',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format='json'):
        flights = Flight.objects.all()
        serializer = FlightSerializer(flights, many=True)

        return Response({
            'status': 'Success',
            'message': 'Flights retrieved',
            'data': serializer.data
        },
        status=status.HTTP_200_OK)


class FlightDetailView(APIView):
    """Flight detail view

    Arguments:
        APIView {view} -- rest_framework API view
    """
    permission_classes = (IsAuthenticated, IsAdminUserOrReadOnly)

    def get(self, request, pk, format='json'):
        flight = get_flight_or_404(pk)
        serializer = FlightSerializer(flight)

        return Response({
            'status': 'Success',
            'message': 'Flight retrieved',
            'data': serializer.data
        },
        status=status.HTTP_200_OK)

    def put(self, request, pk, format='json'):
        flight = get_flight_or_404(pk)
        serializer = FlightSerializer(flight, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response({
                'status': 'Success',
                'message': 'Flight updated',
                'data': serializer.data
            },
            status=status.HTTP_200_OK)
        return Response({
            'status': 'Error',
            'message': 'Could not update flight',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)
