"""M13 — envoie les campagnes approuvées (appelé par le planificateur ou manuellement)."""
from django.core.management.base import BaseCommand

from apps.notifications.models import AwarenessCampaign
from apps.notifications.services import send_campaign


class Command(BaseCommand):
    help = "Envoie les campagnes de sensibilisation approuvées."

    def handle(self, *args, **options):
        total = 0
        for campaign in AwarenessCampaign.objects.filter(status=AwarenessCampaign.Status.APPROVED):
            sent = send_campaign(campaign)
            total += sent
            self.stdout.write(f"{campaign.title} : {sent} envoi(s)")
        self.stdout.write(self.style.SUCCESS(f"Total : {total} envoi(s)"))
