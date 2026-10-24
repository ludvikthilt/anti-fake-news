from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    USER = "user", "Inscrit"
    INSIDER = "insider", "Insider"
    ADMIN = "admin", "Administrateur"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("role", Role.ADMIN)
        extra.setdefault("is_email_verified", True)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.USER)
    is_email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def has_usable_local_password(self):
        return bool(self.password) and not self.password.startswith("!")


class SocialIdentity(models.Model):
    """Identité de connexion externe (Google). Clé de liaison = subject (sub)."""

    provider = models.CharField(max_length=16)  # google
    subject = models.CharField(max_length=255)  # sub Google
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="identities")
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "subject")

    def __str__(self):
        return f"{self.provider}:{self.subject}"


class InsiderRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        ACCEPTED = "accepted", "Acceptée"
        REJECTED = "rejected", "Refusée"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="insider_requests")
    motivation = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Demande insider de {self.user.email} ({self.status})"


class ConsentRecord(models.Model):
    """Consentements séparés par canal (notif_email, notif_telegram, notif_push, awareness_*)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents")
    key = models.CharField(max_length=32)
    version = models.CharField(max_length=16, default="1.0")
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "key")

    def __str__(self):
        return f"{self.user.email}:{self.key}={self.granted}"


class TelegramContact(models.Model):
    """Liaison Telegram : l'utilisateur ouvre le bot avec un code, le chat_id est stocké.

    Aucun numéro de téléphone n'est demandé : Telegram identifie le compte par `chat_id`.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_contact")
    chat_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=64, blank=True)
    link_code = models.CharField(max_length=24, unique=True, null=True, blank=True)
    link_code_expires = models.DateTimeField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    opted_out = models.BooleanField(default=False)
    last_inbound_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telegram de {self.user.email}"


class PushSubscription(models.Model):
    """Abonnement Web Push (PWA) — un par navigateur/appareil."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=64)
    user_agent = models.CharField(max_length=200, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    last_ok_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Push de {self.user.email}"
