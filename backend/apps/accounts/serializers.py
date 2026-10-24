from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import ConsentRecord, InsiderRequest, SocialIdentity

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "name", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Identifiants invalides.")
        if not user.is_active:
            raise serializers.ValidationError("Compte suspendu.")
        attrs["user"] = user
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.CharField()
    nonce = serializers.CharField(required=False, allow_blank=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name", "role", "is_email_verified", "date_joined")
        read_only_fields = fields


class SocialIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialIdentity
        fields = ("id", "provider", "subject", "email", "created_at")


class InsiderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsiderRequest
        fields = ("id", "motivation", "status", "reason", "created_at")
        read_only_fields = ("status", "reason", "created_at")


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ("key", "granted", "version", "granted_at", "withdrawn_at")
