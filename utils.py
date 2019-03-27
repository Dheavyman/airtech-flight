from datetime import datetime
from calendar import timegm
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings

def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function,
    and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    return {
        'user_id': user.pk,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
        'orig_iat': timegm(
            datetime.utcnow().utctimetuple()
        )
    }

def jwt_get_username_from_payload_handler(payload):
    """Get username field

    Arguments:
        payload {dict} -- token payload

    Returns:
        str -- username
    """
    username_field = get_user_model().USERNAME_FIELD
    return payload.get(username_field)
