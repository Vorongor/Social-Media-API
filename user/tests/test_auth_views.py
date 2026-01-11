from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from .test_views_base import BaseAPITestCase

User = get_user_model()


class AuthViewsTestCase(BaseAPITestCase):

    def test_user_registration(self):
        url = reverse("user:create")
        payload = {
            "email": "new@example.com",
            "password": "strongpass"
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_login_returns_jwt_tokens(self):
        url = reverse("user:token_obtain_pair")

        response = self.client.post(url, {
            "email": "user@example.com",
            "password": "password"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_unauthenticated_user_cannot_access_me(self):
        url = reverse("user:manage")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_access_me(self):
        self.authenticate()

        url = reverse("user:manage")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_can_update_own_profile(self):
        self.authenticate()

        url = reverse("user:manage")
        payload = {"first_name": "Updated"}

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
