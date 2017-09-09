from django.http import JsonResponse


class RequestTerminationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        meta = request.META
        consumer_id = meta.get('HTTP_CONSUMER_ID')
        config = meta['BOUNCER_PLUGINS'].get('request-termination')

        if (
            config and (
                not config.get('consumer_id') or
                config.get('consumer_id') == consumer_id
            )
        ):
            return JsonResponse(
                {'message': config['message']},
                status=config['status_code']
            )

        response = self.get_response(request)

        return response
