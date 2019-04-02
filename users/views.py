from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.helpers.auth import get_token
from .models import User
from .serializers import UserSerializer, ImageSerializer


class RegisterView(APIView):
    """
    Register a new user

    Arguments:
        APIView {view} -- rest_framework API view
    """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            saved_user = serializer.save()
            token = get_token(saved_user)
            user_logged_in.send(sender=saved_user.__class__, request=request, user=saved_user)

            return Response({
                'status': 'Success',
                'message': 'User registered',
                'data': {
                    'token': token
                }
            },
            status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Error',
            'message': 'Could not register user',
            'error': serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Login a user

    Arguments:
        APIView {view} -- rest_framework API view
    """

    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({
                'status': 'Error',
                'message': 'Please provide both email and password',
            },
            status=status.HTTP_400_BAD_REQUEST)

        existing_user = authenticate(request, email=email, password=password)
        if existing_user is not None:
            token = get_token(existing_user)
            user_logged_in.send(sender=existing_user.__class__, request=request, user=existing_user)

            return Response({
                'status': 'Success',
                'message': 'Use logged in',
                'data': {
                    'token': token
                }
            },
            status=status.HTTP_200_OK)
        return Response({
            'status': 'Error',
            'message': 'Username or password incorrect',
        },
        status=status.HTTP_401_UNAUTHORIZED)


class ProfilePhotoView(APIView):
    """Profile photo

    Arguments:
        APIView {view} -- rest_framework API view
    """
    def put(self, request, pk, format=None):
        if request.user.id != pk:
            return Response({
                'status': 'Error',
                'message': 'Request forbidden, not users profile'
            },
            status=status.HTTP_403_FORBIDDEN)

        serializer = ImageSerializer(User.objects.get(pk=pk), data=request.data)

        if serializer.is_valid():
            request.user.passport_photo.delete()
            serializer.save()

            return Response({
                'status': 'Success',
                'message': 'Passport photo updated',
                'data': serializer.data
            },
            status=status.HTTP_200_OK)
        return Response({
            'status': 'Error',
            'message': 'Could not update passport photo',
            'error': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = request.user
        if user.id != pk:
            return Response({
                'status': 'Error',
                'message': 'Request forbidden, not users passport photo'
            },
            status=status.HTTP_403_FORBIDDEN)

        if user.passport_photo:
            user.passport_photo.delete()
            return Response({
                'status': 'Success',
                'message': 'Passport photo deleted'
            },
            status=status.HTTP_200_OK)
        return Response({
            'status': 'Error',
            'message': 'User does not have a passport_photo'
        },
        status=status.HTTP_404_NOT_FOUND)
