import re
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

def validate_name(name):
    if re.search(r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$", name) is None:
        print('this happened')
        raise serializers.ValidationError(
            "Name must contain only alphabets, space and characters ',.-")

def get_token(user):
    return jwt_encode_handler(jwt_payload_handler(user))
