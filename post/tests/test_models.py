from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from post.models import Post, Comment, Hashtag

User = get_user_model()


class SocialMediaModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.com",
            password="password123"
        )
        if not hasattr(self.user, 'get_display_name'):
            self.user.get_display_name = "testuser"

        self.hashtag = Hashtag.objects.create(name="python")

        self.post = Post.objects.create(
            title="My Awesome Post",
            content="This is the content",
            author=self.user
        )

    def test_hashtag_str(self):
        self.assertEqual(str(self.hashtag), "python")

    def test_post_creation(self):
        self.assertEqual(self.post.title, "My Awesome Post")
        self.assertTrue(self.post.is_posted)
        self.assertEqual(self.post.author, self.user)

    def test_post_get_image_name(self):
        self.assertEqual(self.post.get_image_name, "post-my-awesome-post")

    def test_post_hashtags(self):
        self.post.hashtags.add(self.hashtag)
        self.assertEqual(self.post.hashtags.count(), 1)
        self.assertIn(self.hashtag, self.post.hashtags.all())

    def test_comment_short_representation(self):
        short_content = "Hello world"
        comment = Comment.objects.create(
            content=short_content,
            commentator=self.user,
            post=self.post
        )
        expected = f"{self.user.get_display_name} say: {short_content}..."
        self.assertEqual(comment.get_short_repr, expected)

    def test_comment_long_representation_truncation(self):
        long_content = "a" * 100
        comment = Comment.objects.create(
            content=long_content,
            commentator=self.user,
            post=self.post
        )
        self.assertEqual(len(comment.get_short_repr.split("say: ")[1]),
                         48)

    def test_comment_full_representation(self):
        comment = Comment.objects.create(
            content="Full content test",
            commentator=self.user,
            post=self.post
        )
        full_repr = comment.get_full_repr
        self.assertIn("Full content test", full_repr)
        self.assertIn(str(self.user.get_display_name), full_repr)