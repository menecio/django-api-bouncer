import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

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

    def test_bounce_api_key_in_body(self):
        """
        Ensure we can perform requests on an api using a valid key sent on
        request body.
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'key-auth',
            'config': {
                'anonymous': '',
                'key_names': ['apikey'],
                'key_in_body': True,
                'hide_credentials': False,
            }
        }
        self.client.post(self.key_auth_url, data, format='json')
        response = self.client.post(self.consumer_key_url)
        self.client.logout()
        apikey = response.data['key']

        url = '/post'
        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.post(
            url,
            data={'apikey': apikey},
            format='json'
        )
        content = response.content.decode('utf-8')
        data = json.loads(content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data['headers']['X-Consumer-Username'],
            self.consumer.username
        )

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
