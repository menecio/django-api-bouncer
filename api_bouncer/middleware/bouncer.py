from ..models import Plugin


class BouncerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST')

        plugin_values = (
            Plugin.objects.filter(
                api__hosts__contains=[host]
            ).values('name', 'config')
        )
        plugins = {p['name']: p['config'] for p in plugin_values}

        request.META['BOUNCER_PLUGINS'] = plugins
        response = self.get_response(request)

        return response
