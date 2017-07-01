from django.http import JsonResponse

from ..models import (
    ConsumerKey,
    Plugin,
)


class KeyAuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST')
        plugin_conf = Plugin.objects.filter(
            api__hosts__contains=[host],
            name='key-auth'
        ).first()

        if plugin_conf:
            config = plugin_conf.config
            apikey = self.get_key(request, config['key_names'])

            if not self.verify_key(request, config, apikey):
                return JsonResponse(
                    data={'error': 'Unauthorized'},
                    status=403
                )

        response = self.get_response(request)

        return response

    def verify_key(self, request, config, key):
        if not key and config.get('key_in_body'):
            key = request.body.get('key')

        c_key = (
            ConsumerKey.objects.select_related('consumer')
                .filter(key=key).first()
        )

        if c_key:
            request.META['X-Consumer-Username'] = c_key.consumer.username
            request.META['X-Consumer-Id'] = c_key.consumer.id

            return True

        return False

    def get_key(self, request, key_names):
        for n in key_names:
            name = n.upper().replace('-', '_')
            key_name = 'HTTP_{0}'.format(name)
            if key_name in request.META:
                return request.META[key_name]

        return None

