import pytest

from apps.accounts.models import User
from apps.analyses.models import Analysis
from apps.notifications.models import Notification
from apps.notifications.services import notify_analysis_done


@pytest.mark.django_db
def test_notify_analysis_done_creates_in_app_notification():
    user = User.objects.create_user(email="n@test.fr", password="pass12345")
    analysis = Analysis.objects.create(
        input_type="text",
        input_text="une information",
        result={"status_label": "Corroborée"},
    )
    notify_analysis_done(user, analysis)
    assert Notification.objects.filter(user=user, kind="analysis_done").count() == 1
    assert analysis.public_id in Notification.objects.get().body
