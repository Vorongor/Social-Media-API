from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from post.models import Post
from post.tasks import publish_scheduled_posts

User = get_user_model()


class PostTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="taskuser@gmail.com",
            password="password"
        )

        self.due_post = Post.objects.create(
            title="Due Post",
            content="Content",
            author=self.user,
            is_posted=False,
            planned_post_time=timezone.now() - timedelta(hours=1)
        )

        self.future_post = Post.objects.create(
            title="Future Post",
            content="Content",
            author=self.user,
            is_posted=False,
            planned_post_time=timezone.now() + timedelta(hours=1)
        )

        self.already_posted = Post.objects.create(
            title="Old Post",
            content="Content",
            author=self.user,
            is_posted=True,
            planned_post_time=timezone.now() - timedelta(days=1)
        )

    def test_publish_scheduled_posts_logic(self):
        """Test that only due posts are published."""

        result = publish_scheduled_posts()

        self.due_post.refresh_from_db()
        self.future_post.refresh_from_db()
        self.already_posted.refresh_from_db()

        self.assertTrue(self.due_post.is_posted)
        self.assertFalse(self.future_post.is_posted)
        self.assertTrue(self.already_posted.is_posted)

        self.assertEqual(result, "Published 1 posts")
