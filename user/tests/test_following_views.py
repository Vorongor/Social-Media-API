from django.urls import reverse
from rest_framework import status

from .test_views_base import BaseAPITestCase


class FollowingViewsTestCase(BaseAPITestCase):

    def test_following_list_requires_authentication(self):
        url = reverse("user:following")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_following_list_returns_followed_users(self):
        self.user.followers.add(self.other_user)
        self.authenticate()

        url = reverse("user:following")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_subscribers_list_returns_followers(self):
        self.other_user.followers.add(self.user)
        self.authenticate()

        url = reverse("user:subscribers")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
