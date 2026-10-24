from rest_framework import serializers

from .models import Analysis, Certification, MissingService, Source


class AnalysisCreateSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_blank=True)  # base64 (data URL)

    class Meta:
        model = Analysis
        fields = ("input_type", "input_text", "input_url", "image")

    def validate(self, attrs):
        input_type = attrs.get("input_type")
        if input_type == Analysis.InputType.TEXT and not attrs.get("input_text", "").strip():
            raise serializers.ValidationError("Le texte est vide.")
        if input_type == Analysis.InputType.LINK and not attrs.get("input_url", "").strip():
            raise serializers.ValidationError("Le lien est vide.")
        if input_type == Analysis.InputType.IMAGE:
            if not attrs.get("image", ""):
                raise serializers.ValidationError("L'image est absente.")
            from .images import validate_data_url

            try:
                validate_data_url(attrs["image"])
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        if len(attrs.get("input_text", "")) > 5000:
            raise serializers.ValidationError("Texte trop long : 5 000 caractères maximum.")
        return attrs


class AnalysisListSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    status_short = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = ("id", "public_id", "input_type", "status", "status_label", "status_short", "created_at")

    def get_status_label(self, obj):
        return obj.result.get("status_label", "") if obj.result else ""

    def get_status_short(self, obj):
        return obj.result.get("status", "") if obj.result else ""


class AnalysisDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ("id", "public_id", "input_type", "status", "result", "created_at", "updated_at")


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ("id", "target_type", "target_id", "verdict", "comment", "source_url", "created_at")
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        if not attrs.get("source_url", "").strip():
            raise serializers.ValidationError("Une source est obligatoire pour certifier ou contester.")
        return attrs
