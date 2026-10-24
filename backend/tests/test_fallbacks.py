import pytest

from apps.analyses import providers
from apps.analyses.orchestrator import providers_run
from apps.core.services import breaker


class NoKey(providers.BaseProvider):
    name = "NoKey"
    account = "nokey"

    def call(self, payload, timeout=8):
        raise providers.ProviderUnavailable("clé NoKey absente")


class Broken(providers.BaseProvider):
    name = "Broken"
    account = "broken"

    def call(self, payload, timeout=8):
        raise RuntimeError("boom")


class Manual(providers.BaseProvider):
    name = "Manual"
    account = "manual"

    def call(self, payload, timeout=8):
        return {"kind": "text", "items": [], "manual": True}


@pytest.fixture(autouse=True)
def _reset_breaker():
    breaker._open_until.clear()
    yield
    breaker._open_until.clear()


@pytest.mark.django_db
def test_fallback_missing_key_reaches_manual():
    out = providers_run([NoKey(), Manual()], {"query": "x"})
    assert out.get("provider") == "Manual"
    assert out.get("manual") is True
    reasons = [m["reason"] for m in out.get("missing", [])]
    assert any("clé NoKey absente" in r for r in reasons)
    # une clé absente ne doit pas ouvrir le coupe-circuit
    assert not breaker.is_open("nokey")


@pytest.mark.django_db
def test_circuit_breaker_opens_on_real_failure():
    providers_run([Broken(), Manual()], {"query": "x"})
    assert breaker.is_open("broken")
    out2 = providers_run([Broken(), Manual()], {"query": "x"})
    reasons = [m["reason"] for m in out2.get("missing", [])]
    assert any("coupe-circuit" in r for r in reasons)


@pytest.mark.django_db
def test_full_text_retrieval(settings):
    from apps.knowledge.models import KnowledgeChunk
    from apps.knowledge.services import retrieve

    # Sans clé Gemini : le RAG doit retomber sur le plein texte tsvector.
    settings.GEMINI_API_KEY = ""

    KnowledgeChunk.objects.create(
        ref_type="wiki",
        ref_id="1",
        title="Les quatre statuts",
        content="Les statuts possibles sont : corroborée, non corroborée, contredite, indéterminée.",
    )
    hits = retrieve("Quels sont les statuts possibles ?")
    assert hits
    assert hits[0].title == "Les quatre statuts"
