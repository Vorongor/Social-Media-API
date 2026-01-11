from django.conf import settings

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils.translation import gettext as _

from base.utils import get_path_for_image


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to=get_path_for_image,
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        symmetrical=False,
        related_name="subscribers",
        blank=True,
    )
    user_name = models.CharField(
        max_length=63,
        blank=True,
        null=True,
    )


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_display_name(self):
        if self.user_name:
            return self.user_name
        if self.first_name:
            return f"{self.first_name} {self.last_name or ''}".strip()
        return self.email.split('@')[0]

    @staticmethod
    def get_dir_path() -> str:
        return "uploads/profile_pictures/"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
