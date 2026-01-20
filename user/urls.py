from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

from user.views import (
    CreateUserView,
    ManageUserView,
    UserProfileViewSet,
    FollowingListView,
    SubscribeListView,
)

router = SimpleRouter()
router.register("", UserProfileViewSet, basename="user")

urlpatterns = [
                  path("auth/register/", CreateUserView.as_view(),
                       name="create"),
                  path("auth/login/", TokenObtainPairView.as_view(),
                       name="token_obtain_pair"),
                  path("auth/logout/", TokenBlacklistView.as_view(),
                       name="token_blacklist"),
                  path("auth/token/refresh/", TokenRefreshView.as_view(),
                       name="token_refresh"),
                  path("auth/token/verify/", TokenVerifyView.as_view(),
                       name="token_verify"),
                  path("auth/me/", ManageUserView.as_view(), name="manage"),
                  path("following/", FollowingListView.as_view(),
                       name="following"),
                  path("subscribers/", SubscribeListView.as_view(),
                       name="subscribers"),
              ] + router.urls

app_name = "user"
