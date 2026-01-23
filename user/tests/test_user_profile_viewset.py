from django.urls import reverse
from rest_framework import status

from .test_views_base import BaseAPITestCase


class UserProfileViewSetTestCase(BaseAPITestCase):

    def test_list_users_excludes_self(self):
        self.authenticate()

        url = reverse("user:user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u["email"] for u in response.data]
        self.assertNotIn(self.user.email, emails)

    def test_retrieve_user_profile(self):
        self.authenticate()

        url = reverse("user:user-detail", args=[self.other_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.other_user.email)

    def test_search_user_by_first_name(self):
        self.authenticate()

        url = reverse("user:user-list")
        response = self.client.get(url, {"search": "Alice"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_follow_user(self):
        self.authenticate()

        url = reverse("user:user-follow", args=[self.other_user.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_followed"])

    def test_unfollow_user(self):
        self.user.followers.add(self.other_user)
        self.authenticate()

        url = reverse("user:user-follow", args=[self.other_user.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_followed"])

    def test_cannot_follow_self(self):
        self.authenticate()

        url = reverse("user:user-follow", args=[self.user.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
