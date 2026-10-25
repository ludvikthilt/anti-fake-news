from rest_framework import serializers

from .models import SiteProfile, WikiPage, WikiRevision


class SiteProfileSerializer(serializers.ModelSerializer):
    """Fiche de site avec l'état de sa reconnaissance automatique."""

    certified_at = serializers.SerializerMethodField()
    system_validations = serializers.SerializerMethodField()
    system_quota = serializers.SerializerMethodField()
    system_remaining = serializers.SerializerMethodField()
    insider_certifications = serializers.SerializerMethodField()
    insider_contests = serializers.SerializerMethodField()
    insider_net = serializers.SerializerMethodField()
    insider_quota = serializers.SerializerMethodField()
    insider_remaining = serializers.SerializerMethodField()

    class Meta:
        model = SiteProfile
        fields = (
            "domain", "name", "nature", "score", "description",
            "certified", "certified_at", "system_validations", "system_quota",
            "system_remaining", "insider_certifications", "insider_contests",
            "insider_net", "insider_quota", "insider_remaining",
        )

    def _state(self, obj):
        cached = getattr(obj, "_site_state", None)
        if cached is None:
            from .sites import evaluation

            cached = evaluation(obj)
            obj._site_state = cached
        return cached

    def get_certified_at(self, obj):
        return self._state(obj)["certified_at"]

    def get_system_validations(self, obj):
        return self._state(obj)["system_validations"]

    def get_system_quota(self, obj):
        return self._state(obj)["system_quota"]

    def get_system_remaining(self, obj):
        return self._state(obj)["system_remaining"]

    def get_insider_certifications(self, obj):
        return self._state(obj)["insider_certifications"]

    def get_insider_contests(self, obj):
        return self._state(obj)["insider_contests"]

    def get_insider_net(self, obj):
        return self._state(obj)["insider_net"]

    def get_insider_quota(self, obj):
        return self._state(obj)["insider_quota"]

    def get_insider_remaining(self, obj):
        return self._state(obj)["insider_remaining"]


class WikiPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiPage
        fields = ("slug", "title", "review_status", "published", "updated_at")


class WikiSubmissionSerializer(serializers.ModelSerializer):
    """Proposition d'un insider : titre + contenu seulement, la publication
    reste décidée par un administrateur."""

    class Meta:
        model = WikiPage
        fields = ("title", "content")

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le titre est obligatoire.")
        return value.strip()


class WikiPageDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True, default="")
    author_email = serializers.CharField(source="author.email", read_only=True, default="")

    class Meta:
        model = WikiPage
        fields = (
            "slug", "title", "content", "published", "review_status", "review_note",
            "author_name", "author_email", "created_at", "updated_at",
        )


class WikiRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiRevision
        fields = ("id", "title", "content", "created_at")
