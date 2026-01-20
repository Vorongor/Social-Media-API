from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer, UserProfileSerializer


@extend_schema(tags=["Authentication"])
class CreateUserView(generics.CreateAPIView):
    """Register a new user in the system."""
    authentication_classes = []
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Get current user profile",
        tags=["User Profile"]
    ),
    put=extend_schema(
        summary="Update current user profile (Full)",
        tags=["User Profile"]
    ),
    patch=extend_schema(
        summary="Update current user profile (Partial)",
        tags=["User Profile"]
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user's own profile and account data."""
    serializer_class = UserProfileSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Social"], summary="List users I follow")
class FollowingListView(generics.ListAPIView):
    """Returns a list of users that the current
    authenticated user is following."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.followers.all().prefetch_related(
            "subscribers", "followers")


@extend_schema(tags=["Social"], summary="List my subscribers")
class SubscribeListView(generics.ListAPIView):
    """Returns a list of users who are
    following the current authenticated user."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscribers.all().prefetch_related(
            "subscribers", "followers")


@extend_schema_view(
    list=extend_schema(
        summary="Search and list user profiles",
        tags=["User Profile"]
    ),
    retrieve=extend_schema(
        summary="Get specific user profile",
        tags=["User Profile"]
    ),
)
class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View and search all user profiles except your own.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["user_name", "first_name", "last_name"]
    filterset_fields = ["user_name", "first_name", "last_name"]
    ordering_fields = ["first_name", "last_name"]

    def get_queryset(self):
        queryset = self.queryset
        me = self.request.user
        return queryset.exclude(id=me.id)

    @extend_schema(
        tags=["Social"],
        summary="Follow/Unfollow a user",
        description="Toggle following status for a specific user by ID.",
        responses={200: {"type": "object", "properties": {
            "user": {"type": "string"},
            "is_followed": {"type": "boolean"},
            "followers_count": {"type": "integer"}
        }}}
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="follow"
    )
    def follow(self, request, pk=None):
        target_user = self.get_object()
        me = request.user

        if me.followers.filter(id=target_user.id).exists():
            me.followers.remove(target_user)
            is_followed = False
        else:
            me.followers.add(target_user)
            is_followed = True

        return Response(
            {
                "user": target_user.user_name,
                "is_followed": is_followed,
                "followers_count": target_user.subscribers.count()
            },
            status=status.HTTP_200_OK,
        )
