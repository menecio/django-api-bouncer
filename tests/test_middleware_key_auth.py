import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from api_bouncer.models import Api, Consumer

User = get_user_model()


class KeyAuthMiddlewareTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'john',
            'john@localhost.local',
            'john123john'
        )
        self.example_api = Api.objects.create(
            name='httpbin',
            hosts=['httpbin.org'],
            upstream_url='https://httpbin.org'
        )
        self.key_auth_url = '/apis/{}/plugins/'.format(self.example_api.name)

        self.consumer = Consumer.objects.create(username='django')
        self.consumer_key_url = (
            '/consumers/{}/key-auth/'.format(self.consumer.username)
        )

    def test_bounce_api_authorization_ok(self):
        """
        Ensure we can perform requests on an api using a valid key.
        """
        self.client.login(username='john', password='john123john')
        self.client.post(self.key_auth_url)
        response = self.client.post(self.consumer_key_url)
        self.client.logout()
        apikey = response.data['key']

        url = '/get?msg=Bounce'
        self.client.credentials(HTTP_HOST='httpbin.org', HTTP_APIKEY=apikey)
        response = self.client.get(url)
        content = response.content.decode('utf-8')
        data = json.loads(content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['args']['msg'], 'Bounce')

    def test_bounce_api_authorization_invalid(self):
        """
        Ensure we can't perform requests on an api without using a valid key.
        """
        self.client.login(username='john', password='john123john')
        self.client.post(self.key_auth_url, {'name': 'key-auth'})
        response = self.client.post(self.consumer_key_url)
        self.client.logout()
        apikey = 'you_know_nothing'

        url = '/get'
        self.client.credentials(HTTP_HOST='httpbin.org', HTTP_APIKEY=apikey)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
