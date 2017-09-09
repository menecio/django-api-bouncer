import re

from django.http import HttpResponse, JsonResponse
from requests import Request, Session
from rest_framework import (
    mixins,
    permissions,
    response,
    status,
    viewsets,
)
from rest_framework.decorators import detail_route

from .models import (
    Api,
    Consumer,
    ConsumerACL,
    ConsumerKey,
    Plugin,
)
from .schemas import (
    defaults,
    plugins,
)
from .serializers import (
    ApiSerializer,
    BouncerSerializer,
    ConsumerACLSerializer,
    ConsumerKeySerializer,
    ConsumerSerializer,
    PluginSerializer,
)


def api_bouncer(request):
    def get_headers(meta):
        """Get all headers beginning with HTTP_ and that have a value"""
        regex = re.compile(r'^HTTP_')
        return {
            (regex.sub('', k)).replace('_', '-'): v
            for k, v in meta.items()
            if k.startswith('HTTP_') and v
        }

    dest_host = request.META.get('HTTP_HOST')
    api = Api.objects.filter(hosts__contains=[dest_host]).first()

    if not api:
        return JsonResponse(data={}, status=status.HTTP_200_OK)

    serializer = BouncerSerializer(data={
        'api': api.name,
        'headers': get_headers(request.META),
    })

    if serializer.is_valid():
        url = '{0}{1}'.format(api.upstream_url, request.path)
        session = Session()
        req = Request(
            request.method,
            url,
            params=request.GET,
            data=request.POST,
            headers=serializer.data['headers']
        )
        prepped = session.prepare_request(req)
        resp = session.send(prepped)
        content_type = resp.headers.get('content-type', 'text/html')

        return HttpResponse(
            content=resp.content,
            content_type=content_type,
            status=resp.status_code,
        )

    return JsonResponse(
        data={'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


class ApiViewSet(viewsets.ModelViewSet):
    serializer_class = ApiSerializer
    queryset = Api.objects.prefetch_related('plugins').all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]
    lookup_field = 'name'

    @detail_route(
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
        url_path='plugins'
    )
    def add_plugin(self, request, name=None):
        api = self.get_object()
        plugin_name = request.data.get('name')
        plugin_conf = request.data.get('config')

        if plugin_name not in plugins:
            return response.Response(
                {'errors': 'Invalid plugin name'},
                status.HTTP_400_BAD_REQUEST
            )

        if not plugin_conf:
            plugin_conf = defaults[plugin_name]

        api_plugin = api.plugins.filter(name=plugin_name).first()
        api_plugin_conf = api_plugin and api_plugin.config or {}
        api_plugin_conf.update(plugin_conf)

        data = {
            'api': api,
            'name': plugin_name,
            'config': api_plugin_conf,
        }

        if not api_plugin:
            api_plugin = Plugin(**data)

        serializer = PluginSerializer(api_plugin, data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return response.Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )


class ConsumerViewSet(viewsets.ModelViewSet):
    serializer_class = ConsumerSerializer
    queryset = Consumer.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]
    lookup_field = 'username'

    @detail_route(
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
        url_path='key-auth',
    )
    def add_key_auth(self, request, username=None):
        consumer = self.get_object()
        data = {
            'consumer': consumer.username,
            'key': request.data.get('key'),
        }
        serializer = ConsumerKeySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return response.Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )

    @detail_route(
        methods=['POST'],
        permission_classes=[permissions.IsAdminUser],
        url_path='acls',
    )
    def add_consumer_acl(self, request, username=None):
        consumer = self.get_object()
        data = {
            'consumer': consumer.username,
            'group': request.data.get('group'),
        }
        serializer = ConsumerACLSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return response.Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )


class ConsumerACLViewSet(viewsets.ModelViewSet):
    serializer_class = ConsumerACLSerializer
    queryset = ConsumerACL.objects.all()
    permission_classes = [permissions.IsAdminUser]


class ConsumerKeyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ConsumerKeySerializer
    queryset = ConsumerKey.objects.all()
    permission_classes = [permissions.IsAdminUser]


class PluginViewSet(viewsets.ModelViewSet):
    serializer_class = PluginSerializer
    queryset = Plugin.objects.all()
    permission_classes = [permissions.IsAdminUser]
