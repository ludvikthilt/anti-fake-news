from rest_framework import serializers

from .models import SiteProfile, WikiPage, WikiRevision


class SiteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteProfile
        fields = ("domain", "name", "nature", "score", "description", "certified")


class WikiPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiPage
        fields = ("slug", "title", "updated_at")


class WikiPageDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True, default="")

    class Meta:
        model = WikiPage
        fields = ("slug", "title", "content", "published", "author_name", "updated_at")


class WikiRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiRevision
        fields = ("id", "title", "content", "created_at")
