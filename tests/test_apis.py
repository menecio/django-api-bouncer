from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from api_bouncer.models import Api

User = get_user_model()


class ApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'john',
            'john@localhost.local',
            'john123john'
        )

    def test_create_api(self):
        """
        Ensure we can create a new api object.
        """
        url = '/apis/'
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Api.objects.count(), 1)
        self.assertEqual(Api.objects.get().name, 'example-api')
