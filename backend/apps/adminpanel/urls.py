from django.urls import path

from .views import (
    AdminStatsView,
    CampaignAdminView,
    CampaignSendView,
    CertificationAdminView,
    InsiderRequestAdminView,
    InternalSendCampaignsView,
    SiteAdminView,
    SiteRecognitionAdminView,
    UserAdminView,
    WikiPendingAdminView,
    WikiReviewAdminView,
)

urlpatterns = [
    path("admin/stats/", AdminStatsView.as_view()),
    path("admin/insider-requests/", InsiderRequestAdminView.as_view()),
    path("admin/insider-requests/<int:pk>/", InsiderRequestAdminView.as_view()),
    path("admin/certifications/", CertificationAdminView.as_view()),
    path("admin/certifications/<int:pk>/withdraw/", CertificationAdminView.as_view()),
    path("admin/wiki/pending/", WikiPendingAdminView.as_view()),
    path("admin/wiki/<slug:slug>/review/", WikiReviewAdminView.as_view()),
    path("admin/users/<int:pk>/suspend/", UserAdminView.as_view()),
    path("admin/sites/", SiteAdminView.as_view()),
    path("admin/sites/<str:domain>/<str:action>/", SiteRecognitionAdminView.as_view()),
    path("admin/campaigns/", CampaignAdminView.as_view()),
    path("admin/campaigns/<int:pk>/send/", CampaignSendView.as_view()),
    path("internal/campaigns/send/", InternalSendCampaignsView.as_view()),
]
