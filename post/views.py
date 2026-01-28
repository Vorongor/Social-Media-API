from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters, generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from post.models import Post, Comment, PostReaction
from post.serializers import PostSerializer, CommentSerializer


@extend_schema(tags=["Posts"])
class PostsViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "author__id"]
    ordering_fields = ["title", "date_posted"]

    def get_queryset(self):
        queryset = (
            Post.objects
            .select_related("author")
            .prefetch_related("hashtags", "comments")
            .annotate(
                likes=Count(
                    "reactions",
                    filter=Q(
                        reactions__reaction=PostReaction.ReactionType.LIKE
                    ),
                ),
                dislikes=Count(
                    "reactions",
                    filter=Q(
                        reactions__reaction=PostReaction.ReactionType.DISLIKE
                    ),
                ),
            )
        )

        if self.action == "list":
            queryset = queryset.filter(is_posted=True)

        if self.action in ["update", "partial_update", "destroy"]:
            queryset = queryset.filter(author=self.request.user)

        if self.action == "liked_posts":
            queryset = queryset.filter(
                reactions__user=self.request.user,
                reactions__reaction=PostReaction.ReactionType.LIKE,
            ).distinct()

        if self.action == "disliked_posts":
            queryset = queryset.filter(
                reactions__user=self.request.user,
                reactions__reaction=PostReaction.ReactionType.DISLIKE,
            ).distinct()

        return queryset

    def perform_create(self, serializer):
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
        summary="React to a post",
        description="Toggle like or dislike on a post",
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="react",
    )
    def react(self, request, pk=None):
        reaction_type = request.data.get("reaction")

        if reaction_type not in PostReaction.ReactionType.values:
            return Response(
                {"detail": "Invalid reaction type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post = self.get_object()
        user = request.user

        reaction, created = PostReaction.objects.get_or_create(
            user=user,
            post=post,
            defaults={"reaction": reaction_type},
        )

        if not created:
            if reaction.reaction == reaction_type:
                reaction.delete()
                message = "Reaction removed"
            else:
                reaction.reaction = reaction_type
                reaction.save(update_fields=["reaction"])
                message = "Reaction updated"
        else:
            message = "Reaction added"

        return Response(
            {
                "message": message,
                "likes": PostReaction.objects.filter(
                    post=post,
                    reaction=PostReaction.ReactionType.LIKE,
                ).count(),
                "dislikes": PostReaction.objects.filter(
                    post=post,
                    reaction=PostReaction.ReactionType.DISLIKE,
                ).count(),
            }
        )

    @extend_schema(
        summary="List all liked posts",
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="liked-posts",
    )
    def liked_posts(self, request):
        return self.list(request)

    @extend_schema(
        summary="List all liked posts",
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="disliked_posts",
    )
    def disliked_posts(self, request):
        return self.list(request)


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
        return (self.queryset.filter(
            author=self.request.user
        ).prefetch_related("hashtags", "reactions", "comments")
        .select_related("author"))


@extend_schema(tags=["Feed"])
class SubscriptionsListView(generics.ListAPIView):
    """
    Feed of posts from authors that the current user follows.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        subscriptions = self.request.user.followers.all()
        return (self.queryset.filter(
            author__in=subscriptions,
            is_posted=True
        ).prefetch_related("hashtags", "reactions", "comments")
        .select_related("author"))
