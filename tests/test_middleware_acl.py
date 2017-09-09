from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Api, Consumer, ConsumerACL

User = get_user_model()


class ACLMiddlewareTests(APITestCase):
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
        self.url = '/apis/{}/plugins/'.format(self.example_api.name)

        self.consumer = Consumer.objects.create(username='django')
        self.acl = ConsumerACL.objects.create(
            consumer=self.consumer,
            group='group1'
        )

    def test_cant_set_whitelist_and_blacklist(self):
        """
        Ensure we can't set blacklist and whitelist on the same configuration
        """
        self.client.login(username='john', password='john123john')
        data = {
            'name': 'acl',
            'config': {
                'whitelist': ['group1', 'group2'],
                'blacklist': ['group3', ],
            }
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['config'],
            ['Whitelist and blacklist are mutually exclusive']
        )

    def test_whitelist_block_request(self):
        """
        Ensure we block requests from groups not included in whitelist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'acl',
            'config': {
                'whitelist': ['nogroup'],
            }
        }
        response = self.client.post(self.url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_CONSUMER_ID=str(self.consumer.id)
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_whitelist_allow_request(self):
        """
        Ensure we allow requests from groups included in whitelist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'acl',
            'config': {
                'whitelist': ['group1', 'group2', 'anyone', ],
            }
        }
        response = self.client.post(self.url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_CONSUMER_ID=str(self.consumer.id)
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklist_block_request(self):
        """
        Ensure we block requests from groups included in blacklist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'acl',
            'config': {
                'blacklist': ['group1', 'anyone'],
            }
        }
        response = self.client.post(self.url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_CONSUMER_ID=str(self.consumer.id)
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_blacklist_allow_request(self):
        """
        Ensure we allow requests from groups not included in blacklist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'acl',
            'config': {
                'blacklist': ['noone', 'another_group'],
            }
        }
        response = self.client.post(self.url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_HOST='httpbin.org',
            HTTP_CONSUMER_ID=str(self.consumer.id)
        )
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_block_request_without_consumer(self):
        """
        Ensure we block requests from groups included in blacklist
        """
        self.client.login(username='john', password='john123john')
        data_ok = {
            'name': 'acl',
            'config': {
                'whitelist': ['group1', 'anyone'],
            }
        }
        response = self.client.post(self.url, data_ok, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_HOST='httpbin.org')
        response = self.client.get('/get')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
