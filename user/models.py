from django.conf import settings

from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

from django.db import models
from django.utils.translation import gettext as _

from base.utils import get_path_for_image
from user.mangers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(blank=True)
    profile_picture = CloudinaryField(
        "profile_picture",
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
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def get_display_name(self) -> str:
        if self.user_name:
            return self.user_name
        if self.first_name:
            return f"{self.first_name} {self.last_name or ''}".strip()
        return self.email.split("@")[0]

    @staticmethod
    def get_dir_path() -> str:
        return "/profile_pictures/"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
