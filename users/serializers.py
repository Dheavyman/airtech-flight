from rest_framework.serializers import ModelSerializer, CharField, ImageField
from .models import User

from .helpers import validate_name


class UserSerializer(ModelSerializer):
    first_name = CharField(validators=[validate_name])
    last_name = CharField(validators=[validate_name])
    passport_photo = ImageField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name',
                  'passport_photo', 'address', 'phone_number', 'updated_at')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ImageSerializer(ModelSerializer):
    """Image serializer

    Arguments:
        ModelSerializer {serializer} -- Rest framework model serializer
    """
    class Meta:
        model = User
        fields = ('id', 'passport_photo', 'updated_at')