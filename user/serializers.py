from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    following_list = serializers.SerializerMethodField()

    followers_list = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "profile_picture",
            "bio",
            "first_name",
            "last_name",
            "following_list",
            "followers_list",
            "full_name",
            "user_name"
        )
        read_only_fields = ("id", "full_name", "following_list",
                            "followers_list")

    def get_following_list(self, obj):
        return [user.get_display_name for user in obj.followers.all()]

    def get_followers_list(self, obj):
        return [user.get_display_name for user in obj.subscribers.all()]
