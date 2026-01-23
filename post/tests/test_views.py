from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from post.models import Post, Comment, Hashtag

User = get_user_model()


class PostApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user1@mail.com",
                                             password="password")
        self.other_user = User.objects.create_user(email="user2@mail.com",
                                                   password="password")
        self.client.force_authenticate(self.user)

        self.post = Post.objects.create(
            title="Visible Post",
            content="Content",
            author=self.user,
            is_posted=True
        )
        self.hidden_post = Post.objects.create(
            title="Draft",
            content="Hidden",
            author=self.user,
            is_posted=False
        )

    def test_list_posts_filters_unposted(self):
        """Test that 'is_posted=False' posts are hidden in the list view."""
        url = reverse("post:post-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Visible Post")

    def test_like_action_toggle(self):
        """Test the custom 'likes' action adds and removes likes."""
        url = reverse("post:post-likes", kwargs={"pk": self.post.id})

        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["likes"], 1)
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())

        res = self.client.post(url)
        self.assertEqual(res.data["likes"], 0)
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())

    def test_add_comment_to_post(self):
        """Test adding a comment via the detail action on PostsViewSet."""
        url = reverse("post:post-comments", kwargs={"pk": self.post.id})
        payload = {"content": "This is a test comment"}

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().post, self.post)

    def test_manage_own_comment(self):
        """Test retrieving a specific comment via the custom path."""
        comment = Comment.objects.create(
            content="Old content",
            commentator=self.user,
            post=self.post
        )
        url = f"/api/posts/{self.post.id}/comments/{comment.id}/"

        res = self.client.put(url, {"content": "Updated content"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "Updated content")

    def test_cannot_manage_others_comment(self):
        """Ensure get_queryset prevents editing comments from other users."""
        other_comment = Comment.objects.create(
            content="Other's comment",
            commentator=self.other_user,
            post=self.post
        )
        url = f"/api/posts/{self.post.id}/comments/{other_comment.id}/"

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_blog_view(self):
        """Verify the MyBlog view only shows the user's posts."""
        url = reverse("post:my-blog")
        res = self.client.get(url)

        self.assertEqual(len(res.data), 2)