from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer, UserProfileSerializer


class CreateUserView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user


class FollowingListView(generics.ListAPIView):
    """
    List of users that the current user is FOLLOWING.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.followers.all().prefetch_related(
            "subscribers", "followers")


class SubscribeListView(generics.ListAPIView):
    """
    List of users that are following the current user (SUBSCRIBERS).
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscribers.all().prefetch_related(
            "subscribers", "followers")


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and searching user profiles, and following/unfollowing.
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

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow"
    )
    def follow(self, request, pk=None):
        target_user = self.get_object()
        me = request.user

        if target_user == me:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
