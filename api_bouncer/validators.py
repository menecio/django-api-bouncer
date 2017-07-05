import ipaddress

from rest_framework import serializers

from .models import Consumer


class BaseValidator(object):
    def __init__(self, config):
        self.config = config

    def __call__(self):
        # Method should only raise serializer.ValidationError in case of errors
        pass


class IpRestrictionValidator(BaseValidator):
    def __call__(self):
        # Whitelist and blacklist are mutually exclusives
        if self.config['whitelist'] and self.config['blacklist']:
            raise serializers.ValidationError({
                'config': 'Whitelist and blacklist are mutually exclusive',
            })

        # Remove duplicated values
        self.config['whitelist'] = list(set(self.config['whitelist']))
        self.config['blacklist'] = list(set(self.config['blacklist']))

        try:
            [
                ipaddress.ip_network(ip)
                for ip in self.config['whitelist']+self.config['blacklist']
            ]
        except (ipaddress.AddressValueError, ValueError) as err:
            raise serializers.ValidationError({
                'config': err
            })

        # Check valid consumer_id if any given
        if (
            self.config.get('consumer_id') and
            not Consumer.objects.filter(pk=self.config['consumer_id']).first()
        ):
            raise serializers.ValidationError({
                'config': 'Invalid consumer'
            })


validator_classes = {
    'ip-restriction': IpRestrictionValidator,
    'key-auth': BaseValidator,
}
