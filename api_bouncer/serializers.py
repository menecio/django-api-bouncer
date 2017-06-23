import uuid

from rest_framework import serializers

from .models import (
    Api,
    Consumer,
    ConsumerKey,
)


class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Api
        fields = '__all__'
        extra_kwargs = {
            'plugins': {
                'binary': True,
                'default': {},
                'required': False,
            }
        }


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'


class ConsumerKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerKey
        fields = '__all__'
        extra_kwargs = {
            'key': {
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }

    def validate_key(self, value):
        """Verify if no key is given and generate one"""
        if not value:
            value = str(uuid.uuid4()).replace('-', '')
        return value
