from rest_framework import (
    mixins,
    permissions,
    response,
    viewsets,
    status,
)
from rest_framework.decorators import detail_route

from .models import (
    Api,
    Consumer,
    ConsumerKey,
    Plugin,
)
from .schemas import defaults, plugins
from .serializers import (
    ApiSerializer,
    ConsumerSerializer,
    ConsumerKeySerializer,
    PluginSerializer,
)


class ApiViewSet(viewsets.ModelViewSet):
    serializer_class = ApiSerializer
    queryset = Api.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]
    lookup_field = 'name'

    @detail_route(
        methods=['patch', 'put'],
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
            'api': api.id,
            'name': plugin_name,
            'config': api_plugin_conf,
        }

        if api_plugin:
            serializer = PluginSerializer(api_plugin, data=data)
        else:
            serializer = PluginSerializer(data=data)

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


class ConsumerKeyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ConsumerKeySerializer
    queryset = ConsumerKey.objects.all()
    permission_classes = [permissions.IsAdminUser]


class PluginViewSet(viewsets.ModelViewSet):
    serializer_class = PluginSerializer
    queryset = Plugin.objects.all()
    permission_classes = [permissions.IsAdminUser]
