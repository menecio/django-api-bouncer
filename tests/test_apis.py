from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from api_bouncer.models import Api

User = get_user_model()


class ApiTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'john',
            'john@localhost.local',
            'john123john'
        )
        self.user = User.objects.create_user(
            'jane',
            'jane@localhost.local',
            'jane123jane'
        )
        self.url = '/apis/'

    def test_create_api_ok(self):
        """
        Ensure we can create a new api object.
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Api.objects.count(), 1)
        self.assertEqual(Api.objects.get().name, 'example-api')

    def test_create_api_regular_user_403(self):
        """
        Ensure only admin user can create a new api object.
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='jane', password='jane123jane')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_api_unauthenticated_403(self):
        """
        Ensure unauthenticated requests can't create a new api.
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_api_missing_name(self):
        """
        Ensure name is required for api creation
        """
        data = {
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Api.objects.count(), 0)

    def test_create_api_empty_hosts(self):
        """
        Ensure at least one host is required for api creation
        """
        data = {
            'name': 'example-api',
            'hosts': [],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Api.objects.count(), 0)

    def test_create_api_empty_string_hosts(self):
        """
        Ensure that empty strings are not valid hostnames
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com', ''],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Api.objects.count(), 0)

    def test_create_ip4_hosts_not_ok(self):
        """
        Ensure we cant use IPv4 addresses as valid hosts. Only FQDN.
        """
        data = {
            'name': 'example-api',
            'hosts': ['172.10.0.13'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Api.objects.count(), 0)

    def test_create_empty_upstream_not_ok(self):
        """
        Ensure we require upstream_url.
        """
        data = {
            'name': 'example-api',
            'hosts': ['172.10.0.13'],
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Api.objects.count(), 0)

    def test_details_api_ok(self):
        """
        Ensure we can get the details of a api object.
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_get = '{}{}'.format(self.url, 'example-api/')
        response_get = self.client.get(url_get)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_get.data['id'],
            str(Api.objects.all().first().pk)
        )

    def test_details_api_unauthenticated_403(self):
        """
        Ensure we can get the details of an api object only if unauthenticated.
        """
        data = {
            'name': 'example-api',
            'hosts': ['example.com'],
            'upstream_url': 'https://httpbin.org'
        }

        # Log as superuser and create an api and then logout
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        url_get = '{}{}/'.format(self.url, 'example-api')
        response_get = self.client.get(url_get)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)
