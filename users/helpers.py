import re
from rest_framework import serializers

def validate_name(name):
    if re.search(r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$", name) is None:
        print('this happened')
        raise serializers.ValidationError(
            "Name must contain only alphabets, space and characters ',.-")
