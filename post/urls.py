from django.urls import path
from rest_framework.routers import DefaultRouter

from post.views import (
    PostsViewSet,
    MyBlogViewSet,
    SubscriptionsListView,
    CommentViewSet,
)

post_router = DefaultRouter()
post_router.register("", PostsViewSet, basename="post")

urlpatterns = [
    path("my-blog/", MyBlogViewSet.as_view(), name="my-blog"),
    path(
        "subscriptions/",
        SubscriptionsListView.as_view(),
        name="subscriptions"
    ),
    path(
        "<int:post_id>/comments/<int:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
    ),
] + post_router.urls

app_name = "post"
