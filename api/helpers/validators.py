import re
from functools import wraps

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

def validate_name(name):
    if re.search(r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$", name) is None:
        raise serializers.ValidationError(
            "Name must contain only alphabets, space and characters ',.-")

def validate_resource_exist(model, instance):
    """
    Meta-decorator

    :param model: resource model
    :param instance: name of the model instance

    :return: decorator
    """
    def decorator(func):
        """
        return inner function

        :param func: function to decorate

        :return: inner function
        """
        @wraps(func)
        def inner(*args, **kwargs):
            """
            Inner function to replace the decorated function

            :param args: Arguments passed to the function
            :param kwargs: Keyword arguments passed to the function

            :return: Error if resource not found or decorated function
            """
            for key, value in kwargs.items():
                if '_pk' in key:
                    try:
                        obj = model.objects.get(pk=value)
                    except model.DoesNotExist:
                        return Response({
                        'status': 'Error',
                        'message': f'{instance.title()} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND)
            kwargs[instance] = obj

            return func(*args, **kwargs)
        return inner
    return decorator
