from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from post.models import Post, Comment, PostReaction

User = get_user_model()


class PostApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user1@mail.com",
            password="password",
        )
        self.other_user = User.objects.create_user(
            email="user2@mail.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

        self.post = Post.objects.create(
            title="Visible Post",
            content="Content",
            author=self.user,
            is_posted=True,
        )
        self.hidden_post = Post.objects.create(
            title="Draft",
            content="Hidden",
            author=self.user,
            is_posted=False,
        )

    def test_list_posts_filters_unposted(self):
        res = self.client.get(reverse("post:post-list"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Visible Post")

    def test_react_like_toggle(self):
        url = reverse(
            "post:post-react",
            kwargs={"pk": self.post.id},
        )

        res = self.client.post(url, {"reaction": "like"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["likes"], 1)

        self.assertTrue(
            PostReaction.objects.filter(
                post=self.post,
                user=self.user,
                reaction="like",
            ).exists()
        )

        res = self.client.post(url, {"reaction": "like"})
        self.assertEqual(res.data["likes"], 0)

        self.assertFalse(
            PostReaction.objects.filter(
                post=self.post,
                user=self.user,
            ).exists()
        )

    def test_add_comment_to_post(self):
        url = reverse(
            "post:post-comments",
            kwargs={"pk": self.post.id},
        )
        res = self.client.post(
            url,
            {"content": "Test comment"},
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().post, self.post)

    def test_manage_own_comment(self):
        comment = Comment.objects.create(
            content="Old",
            commentator=self.user,
            post=self.post,
        )
        url = f"/api/posts/{self.post.id}/comments/{comment.id}/"

        res = self.client.put(
            url,
            {"content": "Updated"},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        comment.refresh_from_db()
        self.assertEqual(comment.content, "Updated")

    def test_cannot_manage_others_comment(self):
        comment = Comment.objects.create(
            content="Other",
            commentator=self.other_user,
            post=self.post,
        )
        url = f"/api/posts/{self.post.id}/comments/{comment.id}/"

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_my_blog_view(self):
        res = self.client.get(
            reverse("post:my-blog")
        )
        self.assertEqual(len(res.data), 2)
