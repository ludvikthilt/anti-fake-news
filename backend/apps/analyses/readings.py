"""Lectures d'insiders (M8) : signature, statut proposé et effet sur le statut.

Une certification est une lecture humaine signée et sourcée. Elle reste modifiable
et retirable par son auteur ; l'administrateur peut retirer une lecture abusive.
"""

from .models import Certification
from .reliability import refresh_analysis_status


def certification_rows(target_type: str, target_id: str) -> list[dict]:
    """Lectures d'une cible, au format servi au front (et dans `result`)."""
    readings = (
        Certification.objects.filter(target_type=target_type, target_id=str(target_id))
        .select_related("user")
        .order_by("created_at")
    )
    return [
        {
            "id": reading.id,
            "verdict": reading.verdict,
            "proposed_status": reading.proposed_status,
            "comment": reading.comment,
            "source_url": reading.source_url,
            "insider": reading.user.name or reading.user.email if reading.user else "",
            "created_at": reading.created_at.isoformat() if reading.created_at else None,
            "updated_at": reading.updated_at.isoformat() if reading.updated_at else None,
        }
        for reading in readings
    ]


def refresh_analysis(analysis) -> str | None:
    """Applique les lectures courantes au statut du dossier."""
    return refresh_analysis_status(analysis, certification_rows(Certification.TargetType.ANALYSIS, analysis.id))
