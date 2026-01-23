from django.conf import settings
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse

from user.admin import UserAdmin

UserModel = get_user_model()


class MockRequest:
    pass


class UserAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.user_admin = UserAdmin(UserModel, self.site)

        self.superuser = UserModel.objects.create_superuser(
            email="admin@example.com",
            password="adminpass"
        )

        self.client.force_login(self.superuser)

    def test_user_admin_class_used(self):
        self.assertIsInstance(self.user_admin, UserAdmin)

    def test_list_display_configuration(self):
        self.assertEqual(
            self.user_admin.list_display,
            ("email", "first_name", "last_name", "is_staff")
        )

    def test_ordering_configuration(self):
        self.assertEqual(self.user_admin.ordering, ("email",))

    def test_search_fields_configuration(self):
        self.assertEqual(
            self.user_admin.search_fields,
            ("email", "first_name", "last_name")
        )

    def test_fieldsets_configuration(self):
        fieldset_fields = []
        for _, options in self.user_admin.fieldsets:
            fieldset_fields.extend(options["fields"])

        self.assertIn("email", fieldset_fields)
        self.assertIn("password", fieldset_fields)
        self.assertIn("first_name", fieldset_fields)
        self.assertIn("last_name", fieldset_fields)
        self.assertIn("is_staff", fieldset_fields)
        self.assertIn("is_superuser", fieldset_fields)

    def test_add_fieldsets_configuration(self):
        add_fields = self.user_admin.add_fieldsets[0][1]["fields"]

        self.assertIn("email", add_fields)
        self.assertIn("password1", add_fields)
        self.assertIn("password2", add_fields)

    def test_admin_changelist_page_loads(self):
        url = reverse("admin:user_user_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_admin_add_user_page_loads(self):
        url = reverse("admin:user_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_username_field_not_present(self):
        request = MockRequest()
        form = self.user_admin.get_form(request)

        self.assertNotIn("username", form.base_fields)
        self.assertIn("email", form.base_fields)
