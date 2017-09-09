from ..models import Consumer, Plugin


class BouncerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST')
        consumer_id = request.META.get('HTTP_CONSUMER_ID')

        # Attach plugins to request.META
        plugin_values = (
            Plugin.objects.filter(
                api__hosts__contains=[host]
            ).values('name', 'config')
        )
        plugins = {p['name']: p['config'] for p in plugin_values}
        request.META['BOUNCER_PLUGINS'] = plugins

        # Attach consumer to request
        bouncer_consumer = (
            Consumer.objects
                    .prefetch_related('acls')
                    .filter(pk=consumer_id)
                    .first()
        )
        request.META['BOUNCER_CONSUMER'] = bouncer_consumer
        response = self.get_response(request)

        return response
