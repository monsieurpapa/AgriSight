from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()


class OrganizationAccessTests(TestCase):
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
        self.gov = User.objects.create_user(
            username='gov',
            email='gov@example.com',
            password='StrongPass123',
            user_type='government',
            organization=self.org_a
        )

    def test_org_list_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get('/api/v1/organizations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_org_list_government_scoped(self):
        self.client.force_login(self.gov)
        response = self.client.get('/api/v1/organizations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
