from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Api, Consumer

User = get_user_model()


class RequestTerminationMiddlewareTests(APITestCase):
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
        self.plugin_url = '/apis/{}/plugins/'.format(self.example_api.name)

        self.consumer = Consumer.objects.create(username='django')

    def test_plugin_termination_activate_with_defaults(self):
        """
        Ensure that a specific API set to terminate all responses, actually
        does it
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'request-termination',
            'config': {},
        }
        response = self.client.post(self.plugin_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['config']['status_code'],
            status.HTTP_503_SERVICE_UNAVAILABLE
        )
        self.assertEqual(response.data['config']['message'], '')

    def test_plugin_termination_activate_with_custom_config(self):
        """
        Ensure that a specific API set to terminate all responses, actually
        does it
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'request-termination',
            'config': {
                'status_code': status.HTTP_502_BAD_GATEWAY,
                'message': 'Hasta la vista, baby!',
            },
        }
        response = self.client.post(self.plugin_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['config']['status_code'],
            status.HTTP_502_BAD_GATEWAY
        )
        self.assertEqual(
            response.data['config']['message'],
            'Hasta la vista, baby!'
        )

    def test_api_request_termination(self):
        """
        Ensure that a specific API set to terminate all responses, actually
        does it
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'request-termination',
            'config': {},
        }
        response = self.client.post(self.plugin_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.get('/get')
        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

    def test_api_termination_with_custom_config(self):
        """
        Ensure that a specific API set to terminate all responses, actually
        does it
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'request-termination',
            'config': {
                'status_code': status.HTTP_502_BAD_GATEWAY,
                'message': 'Hasta la vista, baby!',
            },
        }
        response = self.client.post(self.plugin_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.get('/get')
        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY
        )
        self.assertEqual(
            response.json()['message'],
            'Hasta la vista, baby!'
        )

    def test_api_termination_for_specific_consumer(self):
        """
        Ensure that a specific API set to terminate all responses, actually
        does it
        """

        self.client.login(username='john', password='john123john')

        # Django can't consume the API anymore
        data = {
            'name': 'request-termination',
            'config': {
                'consumer_id': str(self.consumer.id),
                'message': 'Thanks for the cheese!',
                'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
            },
        }

        response = self.client.post(self.plugin_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Without consumer response should be 200 OK
        self.client.credentials(HTTP_HOST='httpbin.org')

        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_CONSUMER_ID=str(self.consumer.id)
        )

        response = self.client.get('/get')
        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE
        )
