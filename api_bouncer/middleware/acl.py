from django.http import JsonResponse


class ACLMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = request.META['BOUNCER_PLUGINS'].get('acl')

        if config:
            blacklist = config.get('blacklist')
            whitelist = config.get('whitelist')
            consumer = request.META['BOUNCER_CONSUMER']

            if not consumer:
                return JsonResponse({'errors': 'Invalid consumer'}, status=403)

            if not self.check_acl(consumer, blacklist, whitelist):
                return JsonResponse({'errors': 'Forbidden'}, status=403)

        response = self.get_response(request)

        return response

    def check_acl(self, consumer, blacklist, whitelist):
        acls = (
            consumer and
            [g for g in consumer.acls.all().values_list('group', flat=True)]
        )
        if (
            whitelist and set(acls) & set(whitelist) or
            blacklist and not set(acls) & set(blacklist)
        ):
            return True
        return False
