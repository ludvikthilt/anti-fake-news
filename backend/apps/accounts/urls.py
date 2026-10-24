from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    GoogleAuthView,
    GoogleIdentityView,
    IdentitiesView,
    InsiderRequestView,
    LoginView,
    MeView,
    NotificationPreferencesView,
    PushSubscriptionView,
    RegisterView,
    TelegramContactView,
)

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("refresh", TokenRefreshView.as_view()),
    path("google/", GoogleAuthView.as_view()),
    path("me/", MeView.as_view()),
    path("me/identities/", IdentitiesView.as_view()),
    path("me/identities/google/", GoogleIdentityView.as_view()),
    path("insider-requests/", InsiderRequestView.as_view()),
    path("me/notification-preferences/", NotificationPreferencesView.as_view()),
    path("me/telegram/", TelegramContactView.as_view()),
    path("me/push/", PushSubscriptionView.as_view()),
]
