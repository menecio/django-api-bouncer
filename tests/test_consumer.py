from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from api_bouncer.models import Consumer

User = get_user_model()


class ConsumerTests(APITestCase):
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
        self.url = '/consumers/'

    def test_create_consumer_ok(self):
        """
        Ensure we can create a new consumer object.
        """
        data = {
            'username': 'django',
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consumer.objects.count(), 1)
        self.assertEqual(Consumer.objects.get().username, 'django')

    def test_create_consumer_403(self):
        """
        Ensure we can create a new consumer object only as superuser.
        """
        data = {
            'username': 'django',
        }
        self.client.login(username='jane', password='jane123jane')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_consumer(self):
        """
        Ensure we can't duplicate consumer object.
        """
        data = {
            'username': 'django',
        }
        self.client.login(username='john', password='john123john')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consumer.objects.count(), 1)
        self.assertEqual(Consumer.objects.get().username, 'django')

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
