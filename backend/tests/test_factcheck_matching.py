"""Une vérification de faits ne contredit une information que si elle porte sur la même affirmation."""
import pytest

from apps.analyses.orchestrator import _claim_coverage, _parse_factchecks


def _claim(text: str, verdict: str) -> dict:
    return {
        "text": text,
        "claimReview": [{"textualRating": verdict, "url": "https://exemple.cm/fc", "publisher": {"name": "AFP Factuel"}}],
    }


def test_unrelated_claim_is_dropped():
    query = "la can 2025 se déroule au maroc selon la caf"
    items = [_claim("Un stadier marocain décédé après la finale de la CAN au Maroc", "Faux")]

    assert _parse_factchecks(items, query) == []


def test_same_claim_is_kept_and_contradicts():
    query = "le président a annulé les élections législatives de décembre"
    items = [_claim("Le président a annulé les élections législatives de décembre", "Faux")]

    rows = _parse_factchecks(items, query)
    assert len(rows) == 1
    assert rows[0]["contradicts"] is True
    assert rows[0]["organization"] == "AFP Factuel"


def test_positive_verdict_does_not_contradict():
    query = "la caf confirme la tenue de la can au maroc"
    items = [_claim("La CAF confirme la tenue de la CAN au Maroc", "Vrai")]

    rows = _parse_factchecks(items, query)
    assert len(rows) == 1
    assert rows[0]["contradicts"] is False


def test_coverage_is_a_ratio_of_claim_words():
    assert _claim_coverage("la can au maroc", "la can 2025 se joue au maroc") == pytest.approx(1.0)
    assert _claim_coverage("", "peu importe") == 0.0
