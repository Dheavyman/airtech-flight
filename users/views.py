from django.http import Http404
from django.contrib.auth.signals import user_logged_in
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_jwt.settings import api_settings

from .models import User
from .serializers import UserSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# Create your views here.
class Register(APIView):
    """
    Register a new user

    Arguments:
        APIView {serializer} -- API view serializer

    Returns:
        User -- User data
    """

    permission_classes = (AllowAny,)

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            saved_user = serializer.save()
            payload = jwt_payload_handler(saved_user)
            token = jwt_encode_handler(payload)
            user_logged_in.send(sender=saved_user.__class__, request=request, user=saved_user)

            return Response({
                    'status': 'Success',
                    'message': 'User registered',
                    'data': {
                        'token': token
                    }
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
