from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from .models import APIKey

User = get_user_model()


class APIKeyAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.org_a = Organization.objects.create(
            name='Org A',
            organization_type='humanitarian',
            contact_email='a@example.com'
        )
        self.org_b = Organization.objects.create(
            name='Org B',
            organization_type='cooperative',
            contact_email='b@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass123',
            user_type='admin'
        )
        self.user_a = User.objects.create_user(
            username='usera',
            email='usera@example.com',
            password='StrongPass123',
            user_type='humanitarian',
            organization=self.org_a
        )

    def test_api_key_create_scoped_to_org(self):
        self.client.force_login(self.user_a)
        response = self.client.post('/api/v1/api-keys/keys/', {
            'organization': str(self.org_b.id),
            'key_name': 'Key A'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(str(data['organization']), str(self.org_a.id))
        self.assertIn('full_api_key', data)

    def test_api_key_list_scoped_to_org(self):
        APIKey.objects.create(
            organization=self.org_a,
            key_name='Key A',
            key_prefix='aaaa',
            key_hash='hasha'
        )
        APIKey.objects.create(
            organization=self.org_b,
            key_name='Key B',
            key_prefix='bbbb',
            key_hash='hashb'
        )

        self.client.force_login(self.user_a)
        response = self.client.get('/api/v1/api-keys/keys/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
