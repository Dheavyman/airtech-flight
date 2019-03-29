from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, SAFE_METHODS

from .models import Flight
from .serializers import FlightSerializer


class IsAdminUserOrReadOnly(IsAdminUser):
    message = 'Request forbidden, must be an admin'

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


class FlightListView(APIView):
    permission_classes = (IsAdminUserOrReadOnly,)

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
