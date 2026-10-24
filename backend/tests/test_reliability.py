from apps.analyses import reliability as R


def _src(domain, score=90, **kw):
    return {
        "url": f"https://{domain}",
        "domain": domain,
        "title": "",
        "excerpt": "",
        "type": "media",
        "score": score,
        "position": "neutral",
        "date": None,
        "date_origin": "",
        "found_by": "test",
        **kw,
    }


class _FC:
    def __init__(self, contradicts):
        self.contradicts = contradicts


def test_status_corroboree():
    assert R.compute_status([_src("a.com"), _src("b.com")], [], [], False) == R.STATUS_OK


def test_status_non_corroboree():
    assert R.compute_status([_src("a.com")], [], [], False) == R.STATUS_WARN


def test_status_contredite():
    assert R.compute_status([_src("a.com"), _src("b.com")], [_FC(True)], [], False) == R.STATUS_BAD


def test_status_contredite_from_factcheck_dict():
    """Le résultat est un JSON : les fact-checks arrivent en dict, pas en objet."""
    fc = {"organization": "AFP Factuel", "verdict": "Faux", "contradicts": True}
    assert R.compute_status([_src("a.com"), _src("b.com")], [fc], [], False) == R.STATUS_BAD


def test_status_indeterminee_empty_and_essential_missing():
    assert R.compute_status([], [], [], True) == R.STATUS_UNK


def test_status_indeterminee_insider_disagreement():
    certs = [{"verdict": "contest"}, {"verdict": "certify"}]
    assert R.compute_status([_src("a.com"), _src("b.com")], [], certs, False) == R.STATUS_OK


def test_nature_opinion():
    assert R.classify_nature("je pense que c'est bien", False, False, False) == R.NATURE_OPINION


def test_nature_infox():
    assert R.classify_nature("un contenu quelconque", False, True, False) == R.NATURE_INFOX


def test_nature_information():
    assert R.classify_nature("un fait daté et sourcé", True, False, True) == R.NATURE_INFORMATION


def test_nature_rumeur():
    assert R.classify_nature("un contenu quelconque", False, False, False) == R.NATURE_RUMEUR


def test_disorder_desinformation():
    assert R.classify_disorder(R.NATURE_INFOX, ["cette image est fausse"]) == R.DISORDER_DESINFORMATION


def test_disorder_mesinformation():
    assert R.classify_disorder(R.NATURE_INFOX, ["inexact"]) == R.DISORDER_MESINFORMATION


def test_disorder_none_for_non_infox():
    assert R.classify_disorder(R.NATURE_RUMEUR, ["faux"]) is None
