from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from base.utils import get_path_for_image


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    content = models.TextField()
    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name="comments"
    )
    commentator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_short_repr(self) -> str:

        return (f"{self.commentator.get_display_name}"
                f" say: {self.content[:45] if (
                    len(self.content) > 45
                ) else self.content}...")

    @property
    def get_full_repr(self) -> str:
        return (f"{self.commentator.get_display_name} at {self.updated_at}"
                f"write: {self.content} ({self.hashtags})")


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_posted = models.BooleanField(default=True)
    planned_post_time = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    image = models.ImageField(
        upload_to=get_path_for_image,
        blank=True,
        null=True,
    )
    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name="posts"
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_posts"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    date_posted = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def get_dir_path() -> str:
        return "uploads/post_images/"

    @property
    def get_image_name(self):
        return f"post-{slugify(self.title)[:20]}"
