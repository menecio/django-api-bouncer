import uuid

from django.contrib.postgres.fields import (
    ArrayField,
    JSONField,
)
from django.core.validators import RegexValidator
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
        )
    )
    plugins = JSONField(default={}, null=True)
    upstream_url = models.URLField(null=False)


class Consumer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )


class ConsumerKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    consumer = models.ForeignKey('Consumer', on_delete=models.CASCADE)
    key = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )

    class Meta:
        unique_together = ('consumer', 'key')
