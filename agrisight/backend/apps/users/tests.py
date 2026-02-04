from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class UserAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.org_a = Organization.objects.create(
            name='Org A',
            organization_type='humanitarian',
            contact_email='a@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass123',
            user_type='admin'
        )
        self.gov = User.objects.create_user(
            username='gov',
            email='gov@example.com',
            password='StrongPass123',
            user_type='government',
            organization=self.org_a
        )

    def test_non_admin_cannot_create_user(self):
        self.client.force_login(self.gov)
        response = self.client.post('/api/v1/users/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'user_type': 'humanitarian',
            'organization': str(self.org_a.id),
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123'
        })
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_user(self):
        self.client.force_login(self.admin)
        response = self.client.post('/api/v1/users/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'user_type': 'humanitarian',
            'organization': str(self.org_a.id),
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123'
        })
        self.assertEqual(response.status_code, 201)
