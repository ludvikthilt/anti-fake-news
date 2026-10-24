from django.urls import path

from .views import NotificationListView, NotificationReadView, TelegramWebhookView

urlpatterns = [
    path("notifications/", NotificationListView.as_view()),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view()),

    path("webhooks/telegram/", TelegramWebhookView.as_view()),
]
