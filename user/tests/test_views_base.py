from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class BaseAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@example.com",
            password="password",
            first_name="John"
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password",
            first_name="Alice"
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)
