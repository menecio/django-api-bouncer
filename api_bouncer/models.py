import uuid

from django.contrib.postgres.fields import (
    ArrayField,
    JSONField,
)
from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
)
from django.db import models


FQDN_REGEX = (
    '(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)'
)


class Api(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )
    hosts = ArrayField(
        models.CharField(
            max_length=200,
            blank=False,
            null=False,
            validators=[
                RegexValidator(regex=FQDN_REGEX),
            ]
        ),
        validators=[
            MinLengthValidator(1, message='At least one is required'),
        ]
    )
    upstream_url = models.URLField(null=False)

    def __str__(self):
        return self.name


class Consumer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )

    def __str__(self):
        return self.username


class ConsumerACL(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    consumer = models.ForeignKey(
        'Consumer',
        on_delete=models.CASCADE,
        related_name='acls',
        related_query_name='acl'
    )
    group = models.CharField(
        max_length=64,
        blank=False,
        null=False
    )

    class Meta:
        unique_together = ('consumer', 'group')

    def __str__(self):
        return '{}: {}'.format(self.consumer.name, self.group)


class ConsumerKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    consumer = models.ForeignKey('Consumer', on_delete=models.CASCADE)
    key = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(8),
        ]
    )

    class Meta:
        unique_together = ('consumer', 'key')


class Plugin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(
        'Api',
        related_name='plugins',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=32, blank=False, null=False)
    config = JSONField(default={}, null=True)

    class Meta:
        unique_together = ('api', 'name', 'config')

    def __str__(self):
        return '{}-{}'.format(self.api, self.name)
