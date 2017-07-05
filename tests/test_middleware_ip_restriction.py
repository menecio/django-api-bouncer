from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Api, Consumer

User = get_user_model()


class IpRestrictionMiddlewareTests(APITestCase):
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

    def test_cant_set_whitelist_and_blacklist(self):
        """
        Ensure we can't set blacklist and whitelist on the same configuration
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'ip-restriction',
            'config': {
                'whitelist': ['192.168.1.0/24'],
                'blacklist': ['10.10.10.0/24'],
            }
        }
        response = self.client.post(self.key_auth_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['config'],
            ['Whitelist and blacklist are mutually exclusive']
        )

    def test_whitelist_accept_only_valid_ip_networks(self):
        """
        Ensure we only accept valid ip networks
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'whitelist': ['192.168.1.0/24', '2001:db00::0/24'],
                'blacklist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['config']['whitelist']), 2)
        self.assertIn(
            '192.168.1.0/24',
            response.data['config']['whitelist'],
        )
        self.assertIn(
            '2001:db00::0/24',
            response.data['config']['whitelist'],
        )
        data_not_ok = {
            'name': 'ip-restriction',
            'config': {
                'whitelist': ['192.168.1.100/24'],
                'blacklist': [],
            }
        }

        response = self.client.post(
            self.key_auth_url,
            data_not_ok,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data['config'],
            ['192.168.1.100/24 has host bits set']
        )

    def test_blacklist_accept_only_valid_ip_networks(self):
        """
        Ensure we only accept valid ip networks
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'blacklist': ['192.168.1.0/24', '2001:db00::0/24'],
                'whitelist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['config']['blacklist']), 2)
        self.assertIn(
            '192.168.1.0/24',
            response.data['config']['blacklist'],
        )
        self.assertIn(
            '2001:db00::0/24',
            response.data['config']['blacklist'],
        )
        data_not_ok = {
            'name': 'ip-restriction',
            'config': {
                'blacklist': ['192.168.1.100/24'],
                'whitelist': [],
            }
        }

        response = self.client.post(
            self.key_auth_url,
            data_not_ok,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data['config'],
            ['192.168.1.100/24 has host bits set']
        )

    def test_whitelist_block_request(self):
        """
        Ensure we block requests from clients not included in whitelist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'whitelist': ['192.168.1.0/24', '2001:db00::0/24'],
                'blacklist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_whitelist_allow_request(self):
        """
        Ensure we allow requests from clients included in whitelist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'whitelist': ['192.168.1.0/24', '2001:db00::0/24'],
                'blacklist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_X_FORWARDED_FOR='192.168.1.100'
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklist_block_request(self):
        """
        Ensure we block requests from clients included in blacklist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'blacklist': ['192.168.1.0/24', '2001:db00::0/24'],
                'whitelist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_X_FORWARDED_FOR='192.168.1.10')
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_blacklist_allow_request(self):
        """
        Ensure we block requests from clients included in blacklist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'ip-restriction',
            'config': {
                'blacklist': ['192.168.1.0/24', '2001:db00::0/24'],
                'whitelist': [],
            }
        }
        response = self.client.post(self.key_auth_url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_X_FORWARDED_FOR='172.1.10.10'
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
