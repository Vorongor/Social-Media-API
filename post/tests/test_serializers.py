from django.test import TestCase
from django.contrib.auth import get_user_model

from post.models import Post, Hashtag, PostReaction
from post.serializers import PostSerializer

User = get_user_model()


class PostSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.com",
            password="password123",
        )

        self.payload = {
            "title": "New Post",
            "content": "Cool content here",
            "hashtags": ["Python", " Django "],
        }

    def test_post_serialization(self):
        post = Post.objects.create(
            title="Test",
            content="Text",
            author=self.user,
        )
        hashtag = Hashtag.objects.create(name="#logic")
        post.hashtags.add(hashtag)

        serializer = PostSerializer(post)

        self.assertEqual(serializer.data["title"], "Test")
        self.assertEqual(
            serializer.data["author"],
            self.user.get_display_name,
        )
        self.assertIn("#logic", serializer.data["hashtags"])


    def test_create_post_with_hashtags(self):
        serializer = PostSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())

        post = serializer.save(author=self.user)

        hashtag_names = list(
            post.hashtags.values_list("name", flat=True)
        )
        self.assertIn("#python", hashtag_names)
        self.assertIn("#django", hashtag_names)
        self.assertEqual(post.hashtags.count(), 2)

    def test_update_post_hashtags(self):
        post = Post.objects.create(
            title="Old",
            content="Old",
            author=self.user,
        )
        post.hashtags.add(
            Hashtag.objects.create(name="#old")
        )

        serializer = PostSerializer(
            post,
            data={"hashtags": ["NewTag"]},
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()

        post.refresh_from_db()
        self.assertEqual(post.hashtags.count(), 1)
        self.assertEqual(post.hashtags.first().name, "#newtag")

    def test_read_only_fields(self):
        serializer = PostSerializer(
            data={
                **self.payload,
                "likes": 999,
                "dislikes": 999,
                "author": "hacker",
            }
        )
        self.assertTrue(serializer.is_valid())
        post = serializer.save(author=self.user)

        self.assertEqual(
            PostReaction.objects.filter(post=post).count(),
            0,
        )
        self.assertEqual(post.author, self.user)
