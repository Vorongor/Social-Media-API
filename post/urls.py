from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter

from post.views import PostsViewSet, MyBlogViewSet, SubscriptionsListView

post_router = DefaultRouter()
post_router.register("", PostsViewSet, basename="post")

urlpatterns = [
                  path(
                      "my-blog/",
                      MyBlogViewSet.as_view(),
                      name="my-blog"
                  ),
                  path(
                      "subscriptions/",
                      SubscriptionsListView.as_view(),
                      name="subscriptions"
                  )
              ] + post_router.urls

app_name = "post"
