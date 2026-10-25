from django.urls import path

from .views import (
    AnalysisDetailView,
    AnalysisListView,
    CertificationDetailView,
    CertificationView,
    InsiderWorkspaceView,
    MediaImageView,
    StatusView,
)

urlpatterns = [
    path("analyses/", AnalysisListView.as_view()),
    path("analyses/<str:pk>/", AnalysisDetailView.as_view()),
    path("certifications/", CertificationView.as_view()),
    path("certifications/<int:pk>/", CertificationDetailView.as_view()),
    path("insider/workspace/", InsiderWorkspaceView.as_view()),
    path("status/", StatusView.as_view()),
    path("health/", StatusView.as_view()),
    path("media/<str:token>/", MediaImageView.as_view()),
]
