import uuid
import jsonschema

from rest_framework import serializers

from .models import (
    Api,
    Consumer,
    ConsumerKey,
    Plugin,
)
from .schemas import plugins


class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Api
        fields = '__all__'


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


class PluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = '__all__'
        extra_kwargs = {
            'config': {
                'default': {},
            }
        }

    def validate(self, data):
        name = data.get('name')
        if not name or name not in plugins:
            raise serializers.ValidationError('Invalid plugin name')

        plugin_schema = plugins[name]

        try:
            jsonschema.validate(data['config'], plugin_schema)
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError({'config': e})

        return data
