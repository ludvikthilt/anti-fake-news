from django.urls import path

from .views import ChatView, SiteDetailView, SiteListView, WikiDetailView, WikiListView, WikiRevisionsView

urlpatterns = [
    path("chat/", ChatView.as_view()),
    path("sites/", SiteListView.as_view()),
    path("sites/<str:domain>/", SiteDetailView.as_view()),
    path("wiki/pages/", WikiListView.as_view()),
    path("wiki/pages/<slug:slug>/", WikiDetailView.as_view()),
    path("wiki/pages/<slug:slug>/revisions/", WikiRevisionsView.as_view()),
]
