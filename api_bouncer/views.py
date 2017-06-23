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
)

from .serializers import (
    ApiSerializer,
    ConsumerSerializer,
    ConsumerKeySerializer,
)


class ApiViewSet(viewsets.ModelViewSet):
    serializer_class = ApiSerializer
    queryset = Api.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]


class ConsumerViewSet(viewsets.ModelViewSet):
    serializer_class = ConsumerSerializer
    queryset = Consumer.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]

    @detail_route(
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
        url_path='key-auth',
    )
    def add_key_auth(self, request, pk=None):
        consumer = self.get_object()
        data = {
            'consumer': consumer.id,
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
