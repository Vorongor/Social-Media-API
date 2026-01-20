from rest_framework import viewsets, filters, generics
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from post.models import Post
from post.serializers import PostSerializer, CommentSerializer


class PostsViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = {
        "title": ["icontains"],
        "author__id": ["exact"],
    }
    filterset_fields = {
        "title": ["icontains"],
        "content": ["icontains"],

        "published_date": ["lte", "gte"],
    }
    ordering_fields = [
        "title",
        "date_posted",
    ]

    def get_queryset(self):
        queryset = self.queryset.prefetch_related(
            "hashtags",
            "likes",
            "comments",
        ).select_related(
            "author",
        )
        if self.action == "list":
            queryset = queryset.filter(
                is_posted=True
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "PUT", "PATCH", "DELETE"],
        detail=True,
        serializer_class=CommentSerializer,
    )
    def comments(self, request, *args, **kwargs):
        pass

    @action(
        methods=["POST"],
        detail=True,
        name="like",
    )
    def likes(self, request, *args, **kwargs):
        user = request.user
        post = self.get_object()
        message = ""
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


class MyBlogViewSet(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(
            author=self.request.user,
        ).prefetch_related(
            "hashtags",
            "likes",
            "comments",
        ).select_related(
            "author",

        )
        return queryset


class SubscriptionsListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        subscriptions = self.request.user.followers.all()
        queryset = self.queryset.filter(
            author__in=subscriptions,
        ).prefetch_related(
            "hashtags",
            "likes",
            "comments",
        ).select_related(
            "author",

        ).filter(
            is_posted=True
        )
        return queryset
