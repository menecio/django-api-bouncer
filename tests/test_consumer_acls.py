from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api_bouncer.models import Consumer, ConsumerACL

User = get_user_model()


class ConsumerACLTests(APITestCase):
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
        self.consumer_monty = Consumer.objects.create(username='monty')

        self.url = '/consumers/{}/acls/'

    def test_create_consumer_acl(self):
        """
        Ensure we can create a new consumer acl object, with a simple group.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        data = {
            'group': 'group1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerACL.objects.count(), 1)
        self.assertEqual(ConsumerACL.objects.get().consumer.username, 'django')
        self.assertEqual(ConsumerACL.objects.get().group, 'group1')

    def test_create_consumer_acl_cant_duplicate(self):
        """
        Ensure we can't create twice the same consumer acl object
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        data = {
            'group': 'group1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerACL.objects.count(), 1)

        # Try to duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ConsumerACL.objects.count(), 1)

    def test_create_consumer_acl_same_group_different_consumer(self):
        """
        Ensure we can create a acl for the same group for different consumers
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        data = {
            'group': 'group1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerACL.objects.count(), 1)
        self.assertEqual(ConsumerACL.objects.get().consumer.username, 'django')
        self.assertEqual(ConsumerACL.objects.get().group, 'group1')

        url = self.url.format(self.consumer_monty.username)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumerACL.objects.count(), 2)
        self.assertEqual(
            ConsumerACL.objects.get(consumer_id=self.consumer_monty.pk).group,
            'group1'
        )

    def test_create_consumer_acl_group_cant_be_empty(self):
        """
        Ensure we can't create a new consumer acl object, without group.
        """
        self.client.login(username='john', password='john123john')
        url = self.url.format(self.consumer.username)
        data = {
            'group': ''
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ConsumerACL.objects.count(), 0)
