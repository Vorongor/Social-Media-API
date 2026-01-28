from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="strong-password",
            first_name="John",
            last_name="Doe",
            user_name="johnd"
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="strong-password"
        )

    def test_user_created_with_email_as_username(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("strong-password"))
        self.assertIsNone(self.user.username)

    def test_full_name_property(self):
        self.assertEqual(self.user.full_name, "John Doe")

    def test_full_name_with_missing_last_name(self):
        user = User.objects.create_user(
            email="nolast@example.com",
            password="password",
            first_name="Jane"
        )
        self.assertEqual(user.full_name, "Jane None")

    def test_get_display_name_prefers_user_name(self):
        self.assertEqual(self.user.get_display_name, "johnd")

    def test_get_display_name_falls_back_to_first_and_last_name(self):
        user = User.objects.create_user(
            email="name@example.com",
            password="password",
            first_name="Alice",
            last_name="Smith"
        )
        self.assertEqual(user.get_display_name, "Alice Smith")

    def test_get_display_name_falls_back_to_email_prefix(self):
        user = User.objects.create_user(
            email="fallback@example.com",
            password="password"
        )
        self.assertEqual(user.get_display_name, "fallback")

    def test_followers_relationship(self):
        self.other_user.followers.add(self.user)

        self.assertIn(self.user, self.other_user.followers.all())
        self.assertIn(self.other_user, self.user.subscribers.all())

    def test_followers_relationship_is_not_symmetrical(self):
        self.other_user.followers.add(self.user)

        self.assertNotIn(self.other_user, self.user.followers.all())

    def test_optional_fields_are_blank_or_null(self):
        user = User.objects.create_user(
            email="optional@example.com",
            password="password"
        )

        self.assertEqual(user.bio, "")
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.user_name)

    def test_get_dir_path_static_method(self):
        self.assertEqual(
            User.get_dir_path(),
            "/profile_pictures/"
        )
