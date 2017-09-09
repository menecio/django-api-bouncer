import uuid

import jsonschema

from rest_framework import serializers

from . import validators
from .models import (
    Api,
    Consumer,
    ConsumerACL,
    ConsumerKey,
    Plugin,
)
from .schemas import plugins


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'


class ConsumerACLSerializer(serializers.ModelSerializer):
    consumer = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='username',
        queryset=Consumer.objects.all()
    )

    class Meta:
        model = ConsumerACL
        fields = '__all__'
        extra_kwargs = {
            'group': {
                'required': True,
                'allow_null': False,
                'allow_blank': False,
            },
        }


class ConsumerKeySerializer(serializers.ModelSerializer):
    consumer = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='username',
        queryset=Consumer.objects.all()
    )

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
            value = str(uuid.uuid4().int)
        return value


class PluginSerializer(serializers.ModelSerializer):
    api = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )

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
        config = data.get('config', {})

        if not name or name not in plugins:
            raise serializers.ValidationError('Invalid plugin name')

        plugin_schema = plugins[name]

        if self.instance:
            initial_config = self.instance.config
            initial_config.update(config)
            config = initial_config

        try:
            jsonschema.validate(config, plugin_schema)
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError({'config': e})

        plugin_validators = validators.validator_classes.get(name, [])
        for validator in plugin_validators:
            validate = validator(data['config'])
            validate()
        return data


class ApiSerializer(serializers.ModelSerializer):
    plugins = PluginSerializer(
        many=True,
        read_only=False,
        required=False
    )

    class Meta:
        model = Api
        fields = '__all__'


class BouncerSerializer(serializers.Serializer):
    api = serializers.CharField(allow_blank=False, allow_null=False)
    headers = serializers.DictField(child=serializers.CharField())

    def validate_api(self, value):
        api = Api.objects.get(name=value)
        if not api:
            raise serializers.ValidationError('Unknown API')
        return value
