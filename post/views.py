from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters, generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from post.models import Post, Comment
from post.serializers import PostSerializer, CommentSerializer


@extend_schema(tags=["Posts"])
class PostsViewSet(viewsets.ModelViewSet):
    """
    Manage blog posts.
    Provides standard CRUD operations
    and additional actions for likes and comments.
    """
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "author__id"]
    filterset_fields = {
        "title": ["icontains"],
        "content": ["icontains"],
        "published_date": ["lte", "gte"],
    }
    ordering_fields = ["title", "date_posted"]

    def get_queryset(self):
        """
        Optimized queryset with prefetch/select_related.
        Filters out unposted items for the list action.
        """
        queryset = self.queryset.prefetch_related(
            "hashtags", "likes", "comments"
        ).select_related("author")

        if self.action == "list":
            queryset = queryset.filter(is_posted=True)
        if self.action in ["update", "partial_update", "destroy"]:
            queryset = queryset.filter(
                author=self.request.user
            )
        if self.action == "liked-posts":
            queryset = queryset.filter(
                likes=self.request.user
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        """Assign the current user as the author of the post."""
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Add a comment to a post",
        description="Creates a new comment linked to the "
                    "specific post and the current authenticated user.",
        responses={201: CommentSerializer}
    )
    @action(
        methods=["POST"],
        detail=True,
        serializer_class=CommentSerializer,
    )
    def comments(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(commentator=self.request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Toggle like on a post",
        description="Adds a like if not present, "
                    "removes it if it already exists.",
        responses={200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"},
                "likes": {"type": "integer"}
            }
        }
        }
    )
    @action(
        methods=["POST"],
        detail=True,
        name="like",
    )
    def likes(self, request, *args, **kwargs):
        user = request.user
        post = self.get_object()
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            message = "You unliked this post"
        else:
            post.likes.add(user)
            message = "You liked this post"
        return Response({
            "message": message,
            "likes": post.likes.count()
        })

    @extend_schema(
        summary="List all liked posts.",
        description="Retrieve list of liked posts",
    )
    @action(
        methods=["GET"],
        detail=False,
        name="liked-posts",
    )
    def liked_posts(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Posts"])
class CommentViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    Update or delete existing comments.
    Users can only manage comments they created.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Restrict access to comments owned by the user."""
        post_id = self.kwargs.get("post_id")
        return self.queryset.filter(
            commentator=self.request.user,
            post__id=post_id,
        )


@extend_schema(tags=["Feed"])
class MyBlogViewSet(generics.ListAPIView):
    """
    List all posts created by the authenticated user.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return self.queryset.filter(
            author=self.request.user
        ).prefetch_related("hashtags", "likes", "comments").select_related(
            "author")


@extend_schema(tags=["Feed"])
class SubscriptionsListView(generics.ListAPIView):
    """
    Feed of posts from authors that the current user follows.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        subscriptions = self.request.user.followers.all()
        return self.queryset.filter(
            author__in=subscriptions,
            is_posted=True
        ).prefetch_related("hashtags", "likes", "comments").select_related(
            "author")
