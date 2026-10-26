from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from allauth.account.forms import default_token_generator
from rest_framework.test import APIClient
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/registration/"
        self.login_url = "/api/auth/login/"
        self.user_url = "/api/auth/user/"
        self.reset_url = "/api/auth/password/reset/"
        self.reset_confirm_url = "/api/auth/password/reset/confirm/"
        self.change_password_url = "/api/auth/password/change/"
        self.auth_config_url = "/api/auth/config/"

    def test_auth_config_includes_rbac_and_password_rules(self):
        resp = self.client.get(self.auth_config_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("rbac", resp.data)
        self.assertIn("role_permissions", resp.data["rbac"])
        self.assertTrue(resp.data["email_verification_required"])
        self.assertTrue(resp.data["password_requirements"]["require_uppercase"])
        self.assertTrue(resp.data["password_requirements"]["require_lowercase"])
        self.assertTrue(resp.data["password_requirements"]["require_numbers"])

    def test_registration_enforces_password_complexity(self):
        payload = {
            "email": "weak@example.com",
            "password1": "weakpass",
            "password2": "weakpass",
            "first_name": "Weak",
            "last_name": "User",
            "user_type": "researcher",
            "phone_number": ""
        }
        resp = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_registration_sends_verification_email(self):
        payload = {
            "email": "newuser@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "first_name": "New",
            "last_name": "User",
            "user_type": "researcher",
            "phone_number": ""
        }
        resp = self.client.post(self.register_url, payload, format="json")
        self.assertIn(resp.status_code, (200, 201))
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_login_after_email_verification(self):
        user = User.objects.create_user(
            username="verifieduser",
            email="verified@example.com",
            password="StrongPass123",
            user_type="researcher"
        )
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        resp = self.client.post(self.login_url, {"email": user.email, "password": "StrongPass123"}, format="json")
        self.assertEqual(resp.status_code, 200)

        me = self.client.get(self.user_url)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data.get("email"), user.email)

    def test_password_reset_request_sends_email(self):
        user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="StrongPass123",
            user_type="researcher"
        )
        resp = self.client.post(self.reset_url, {"email": user.email}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_password_reset_confirm(self):
        user = User.objects.create_user(
            username="resetconfirm",
            email="resetconfirm@example.com",
            password="StrongPass123",
            user_type="researcher"
        )
        uid = user_pk_to_url_str(user)
        token = default_token_generator.make_token(user)

        payload = {"uid": uid, "token": token, "new_password1": "NewStrongPass123", "new_password2": "NewStrongPass123"}
        resp = self.client.post(self.reset_confirm_url, payload, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_profile_update(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="StrongPass123",
            user_type="researcher"
        )
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        self.client.post(self.login_url, {"email": user.email, "password": "StrongPass123"}, format="json")
        resp = self.client.patch(self.user_url, {"first_name": "Updated"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("first_name"), "Updated")

    def test_change_password(self):
        user = User.objects.create_user(
            username="changepass",
            email="changepass@example.com",
            password="StrongPass123",
            user_type="researcher"
        )
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        self.client.post(self.login_url, {"email": user.email, "password": "StrongPass123"}, format="json")
        payload = {"old_password": "StrongPass123", "new_password1": "ChangedPass123", "new_password2": "ChangedPass123"}
        resp = self.client.post(self.change_password_url, payload, format="json")
        self.assertEqual(resp.status_code, 200)


class RegistrationUsernameRegressionTests(TestCase):
    """
    Regression: login is e-mail based, so allauth never set ``username`` and the
    first sign-up was saved with username=''. Every later sign-up then failed
    with a 500 (unique constraint on users_user.username).
    Report: .gstack/qa-reports/qa-report-agrisight-2026-10-26.md (P0 #2)
    """

    register_url = "/api/auth/registration/"

    def _register(self, email):
        return APIClient().post(self.register_url, {
            "email": email,
            "password1": "Kivu#Harvest2026",
            "password2": "Kivu#Harvest2026",
            "first_name": "Neema",
            "last_name": "Furaha",
            "user_type": "cooperative",
            "phone_number": "",
        }, format="json")

    def test_multiple_signups_succeed_with_unique_usernames(self):
        for email in ("amani@example.com", "neema@example.org", "bahati@example.net"):
            resp = self._register(email)
            self.assertIn(resp.status_code, (200, 201), resp.content)
        usernames = list(User.objects.values_list("username", flat=True))
        self.assertEqual(len(usernames), 3)
        self.assertNotIn("", usernames)
        self.assertEqual(len(set(usernames)), 3)

    def test_same_local_part_gets_distinct_username(self):
        self.assertIn(self._register("amani@ngo-one.org").status_code, (200, 201))
        self.assertIn(self._register("amani@ngo-two.org").status_code, (200, 201))
        u1, u2 = User.objects.order_by("id").values_list("username", flat=True)
        self.assertEqual(u1, "amani")
        self.assertTrue(u2.startswith("amani_") and u2 != u1)

    def test_username_unaffected_by_soft_deleted_user(self):
        old = User.objects.create_user(username="amani", email="old@example.com", password="x", user_type="researcher")
        if hasattr(old, "deleted_at"):
            from django.utils import timezone
            User.all_objects.filter(pk=old.pk).update(deleted_at=timezone.now())
        self.assertIn(self._register("amani@example.com").status_code, (200, 201))
