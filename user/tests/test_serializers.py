from django.test import TestCase
from django.contrib.auth import get_user_model

from user.serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


class UserSerializerTestCase(TestCase):

    def test_create_user_with_valid_data(self):
        payload = {
            "email": "user@example.com",
            "password": "strongpass",
        }

        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertFalse(user.is_staff)

    def test_password_min_length_validation(self):
        payload = {
            "email": "short@example.com",
            "password": "123",
        }

        serializer = UserSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_is_staff_is_read_only(self):
        payload = {
            "email": "staff@example.com",
            "password": "password",
            "is_staff": True,
        }

        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertFalse(user.is_staff)

    def test_update_user_password(self):
        user = User.objects.create_user(
            email="update@example.com",
            password="oldpassword"
        )

        payload = {"password": "newpassword"}

        serializer = UserSerializer(
            instance=user,
            data=payload,
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertTrue(user.check_password("newpassword"))


class UserProfileSerializerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="main@example.com",
            password="password",
            first_name="John",
            last_name="Doe",
            user_name="johnny"
        )

        self.follower = User.objects.create_user(
            email="follower@example.com",
            password="password",
            first_name="Alice"
        )

        self.following = User.objects.create_user(
            email="following@example.com",
            password="password",
            first_name="Bob"
        )

        self.user.followers.add(self.following)
        self.follower.followers.add(self.user)

    def test_profile_serializer_fields(self):
        serializer = UserProfileSerializer(self.user)
        data = serializer.data

        expected_fields = {
            "id",
            "email",
            "profile_picture",
            "bio",
            "first_name",
            "last_name",
            "following_list",
            "followers_list",
            "full_name",
            "user_name",
        }

        self.assertEqual(set(data.keys()), expected_fields)

    def test_full_name_is_read_only(self):
        serializer = UserProfileSerializer(self.user, data={
            "full_name": "Fake Name"
        }, partial=True)

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.full_name, "John Doe")

    def test_following_list_representation(self):
        serializer = UserProfileSerializer(self.user)
        data = serializer.data

        self.assertIn("Bob", data["following_list"])

    def test_followers_list_representation(self):
        serializer = UserProfileSerializer(self.user)
        data = serializer.data

        self.assertIn("Alice", data["followers_list"])

    def test_profile_update_allowed_fields(self):
        payload = {
            "bio": "New bio",
            "first_name": "Updated",
        }

        serializer = UserProfileSerializer(
            instance=self.user,
            data=payload,
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.bio, "New bio")
        self.assertEqual(user.first_name, "Updated")

    def test_email_can_be_updated_if_not_restricted(self):
        payload = {"email": "new@example.com"}

        serializer = UserProfileSerializer(
            instance=self.user,
            data=payload,
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.email, "new@example.com")
