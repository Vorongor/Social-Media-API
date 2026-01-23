from django.test import TestCase
from django.contrib.auth import get_user_model
from post.models import Post, Hashtag
from post.serializers import PostSerializer

User = get_user_model()


class PostSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.com",
            password="password123"
        )
        if not hasattr(self.user, 'get_display_name'):
            self.user.get_display_name = "testuser"

        self.payload = {
            "title": "New Post",
            "content": "Cool content here",
            "hashtags": ["Python", " Django "]
        }

    def test_post_serialization(self):
        """Test that the model instance is correctly converted to a dict."""
        post = Post.objects.create(title="Test", content="Text",
                                   author=self.user)
        hashtag = Hashtag.objects.create(name="#logic")
        post.hashtags.add(hashtag)

        serializer = PostSerializer(post)

        self.assertEqual(serializer.data["title"], "Test")
        self.assertEqual(serializer.data["author"], self.user.get_display_name)
        self.assertIn("#logic", serializer.data["hashtags"])
        self.assertEqual(serializer.data["likes"], 0)

    def test_create_post_with_hashtags(self):
        """Test custom create logic and hashtag normalization."""
        serializer = PostSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())

        post = serializer.save(author=self.user)

        self.assertEqual(post.title, self.payload["title"])
        hashtag_names = list(post.hashtags.values_list("name", flat=True))
        self.assertIn("#python", hashtag_names)
        self.assertIn("#django", hashtag_names)
        self.assertEqual(post.hashtags.count(), 2)

    def test_update_post_hashtags(self):
        """Test that updating hashtags replaces the old ones correctly."""
        post = Post.objects.create(title="Old", content="Old",
                                   author=self.user)
        old_hashtag = Hashtag.objects.create(name="#old")
        post.hashtags.add(old_hashtag)

        update_payload = {
            "title": "Updated Title",
            "hashtags": ["NewTag"]
        }

        serializer = PostSerializer(post, data=update_payload, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        post.refresh_from_db()
        self.assertEqual(post.title, "Updated Title")
        self.assertEqual(post.hashtags.count(), 1)
        self.assertEqual(post.hashtags.first().name, "#newtag")

    def test_read_only_fields(self):
        """Ensure users cannot overwrite read-only fields like 'likes'."""
        malicious_payload = {
            **self.payload,
            "likes": 9999,
            "author": "someone_else"
        }
        serializer = PostSerializer(data=malicious_payload)
        self.assertTrue(serializer.is_valid())
        post = serializer.save(author=self.user)

        self.assertEqual(post.likes.count(), 0)
        self.assertEqual(post.author, self.user)