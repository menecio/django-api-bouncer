from django.http import JsonResponse

from ..models import Plugin


class RequestTerminationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST')
        consumer_id = request.META.get('HTTP_CONSUMER_ID')

        plugin_conf = Plugin.objects.filter(
            api__hosts__contains=[host],
            name='request-termination'
        ).first()

        # import pdb; pdb.set_trace()

        if (
            plugin_conf and (
                not plugin_conf.config.get('consumer_id') or
                plugin_conf.config.get('consumer_id') == consumer_id
            )
        ):
            config = plugin_conf.config
            return JsonResponse(
                {'message': config['message']},
                status=config['status_code']
            )

        response = self.get_response(request)

        return response
