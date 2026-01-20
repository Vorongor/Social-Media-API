from rest_framework import serializers

from post.models import Post, Comment, Hashtag


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        return data


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    comments = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="get_short_repr"
    )
    hashtags = CreatableSlugRelatedField(
        many=True,
        queryset=Hashtag.objects.all(),
        slug_field="name"
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="get_display_name"
    )
    likes = serializers.IntegerField(
        read_only=True,
        source="likes.count",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "is_posted",
            "planned_post_time",
            "likes",
            "author",
            "image",
            "comments",
            "hashtags",
        )
        read_only_fields = (
            "id",
            "likes",
            "comments",
            "author"
        )

    @staticmethod
    def _normalize_hashtag(name: str) -> str:
        return "#" + name.lower().strip()

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        post = Post.objects.create(**validated_data)

        if hashtags_data:
            normalized = [
                self._normalize_hashtag(name)
                for name in hashtags_data
            ]

            hashtags = [
                Hashtag.objects.get_or_create(name=name)[0]
                for name in set(normalized)
            ]

            post.hashtags.set(hashtags)

        return post

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if hashtags_data is not None:
            normalized = [
                self._normalize_hashtag(name)
                for name in hashtags_data
            ]

            hashtags = [
                Hashtag.objects.get_or_create(name=name)[0]
                for name in set(normalized)
            ]

            instance.hashtags.set(hashtags)

        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
        )
