from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from api_bouncer.models import Api

User = get_user_model()


class PluginTests(APITestCase):
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
        self.example_api = Api.objects.create(
            name='example-api',
            hosts=['example.com'],
            upstream_url='https://httpbin.org'
        )

        self.url = '/apis/{}/plugins/'

    def test_api_add_plugin(self):
        """
        Ensure we can add a plugin to an api as superusers.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.example_api.name)

        data = {
            'name': 'key-auth',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.example_api.plugins.count(), 1)
        self.assertEqual(self.example_api.plugins.first().name, data['name'])

    def test_api_add_plugin_403(self):
        """
        Ensure we can add a plugin to an api only as superusers.
        """
        self.client.login(username='jane', password='jane123jane')
        url = self.url.format(self.example_api.name)

        data = {
            'name': 'key-auth',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_add_plugin_wrong_name(self):
        """
        Ensure we can't add a plugin to an api that doesn't exist.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.example_api.name)

        data = {
            'name': 'na-ah',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], 'Invalid plugin name')

    def test_api_add_plugin_modify_partially_config(self):
        """
        Ensure we can partially modify a plugin configuration.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.example_api.name)

        data = {
            'name': 'key-auth',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.example_api.plugins.count(), 1)
        self.assertEqual(self.example_api.plugins.first().name, data['name'])

        expected_res = response.data
        expected_res['config'].update({'anonymous': 'citizen-four'})

        data.update({'config': {'anonymous': 'citizen-four'}})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.example_api.plugins.count(), 1)
        self.assertEqual(response.data, expected_res)

    def test_api_add_plugin_no_extra_keys(self):
        """
        Ensure we can't add arguments not defined on plugin's schema.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.example_api.name)

        data = {
            'name': 'key-auth',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.example_api.plugins.count(), 1)
        self.assertEqual(self.example_api.plugins.first().name, data['name'])

        data.update({'config': {'you_shall_not_pass': True}})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
