from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Consumer, ConsumerKey

User = get_user_model()


class ConsumerKeyTests(APITestCase):
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
        self.consumer = Consumer.objects.create(username='django')

        self.url = '/consumers/{}/key-auth/'

    def test_create_consumer_key_auto(self):
        """
        Ensure we can create a new consumer key object, with a default value.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerKey.objects.count(), 1)
        self.assertEqual(ConsumerKey.objects.get().consumer.username, 'django')

    def test_create_consumer_key_auto_403(self):
        """
        Ensure we can create a new consumer key object with a default value,
        only as superusers.
        """
        url = self.url.format(self.consumer.username)

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_consumer_key_given_key(self):
        """
        Ensure we can create a new consumer key object, with a default value.
        """
        data = {'key': 'abc123456'}
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerKey.objects.count(), 1)
        self.assertEqual(ConsumerKey.objects.get().consumer.username, 'django')
        self.assertEqual(ConsumerKey.objects.get().key, data['key'])

    def test_create_consumer_key_given_key_too_short(self):
        """
        Ensure we can create a new consumer key object, with a default value.
        """
        data = {'key': 'abc123'}
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_consumer_key_given_empty_key(self):
        """
        Ensure we can't create an empty consumer key object, if an empty key is
        given, we must generate a hash for the key
        """
        data = {'key': ''}
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['key'], '')
