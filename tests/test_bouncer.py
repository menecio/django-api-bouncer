from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Api

User = get_user_model()


class BouncerTests(APITestCase):
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

    def test_bounce_api_request(self):
        """
        Ensure we can bouncer a request to an api and get the same response.
        """
        url = '/status/418'  # teapot
        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 418)
        self.assertIn('teapot', response.content.decode('utf-8'))

    def test_bounce_api_request_unknown_host(self):
        """
        Ensure we send a response when the hosts making the request is not
        trying to call an api.
        """
        url = '/test'
        self.client.credentials(HTTP_HOST='the-unknown.com')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {})
