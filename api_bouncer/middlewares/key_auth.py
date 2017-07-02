import json

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
            apikey = self.get_key(
                request,
                config['key_names'],
                config['key_in_body']
            )

            if not self.verify_key(request, config, apikey):
                return JsonResponse(
                    data={'error': 'Unauthorized'},
                    status=403
                )
        response = self.get_response(request)

        return response

    def verify_key(self, request, config, key):
        c_key = (
            ConsumerKey.objects
                       .select_related('consumer')
                       .filter(key=key).first()
        )

        if c_key:
            request.META['HTTP_X_CONSUMER_USERNAME'] = c_key.consumer.username
            request.META['HTTP_X_CONSUMER_ID'] = str(c_key.consumer.id)
            return True
        return False

    def get_key(self, request, key_names, key_in_body=False):
        if key_in_body:
            try:
                body = json.loads(request.body.decode('utf-8'))
                for k in key_names:
                    if k in body:
                        return body[k]
                return None
            except json.JSONDecodeError:
                return None

        for n in key_names:
            name = n.upper().replace('-', '_')
            key_name = 'HTTP_{0}'.format(name)
            if key_name in request.META:
                return request.META[key_name]

        return None
