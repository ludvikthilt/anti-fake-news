from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=32, default="analysis_done")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"


class AwarenessCampaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        APPROVED = "approved", "Approuvée"
        SENT = "sent", "Envoyée"

    class Channel(models.TextChoices):
        EMAIL = "email", "E-mail"
        TELEGRAM = "telegram", "Telegram"
        PUSH = "push", "Notification push (PWA)"

    title = models.CharField(max_length=255)
    body = models.TextField()
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.EMAIL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
