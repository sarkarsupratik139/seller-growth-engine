"""Tests for rulebook.py on the fictional sample reports in sample-data/.

    python3 engine/test_rulebook.py
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import rulebook  # noqa: E402

SAMPLES = HERE.parent / "sample-data"
BRAND = ["sunny shelf", "sunnyshelf"]


def actions_for(name):
    return rulebook.run(rulebook.load(SAMPLES / name), price=399, target_acos=0.30, max_bid=15, current_bid=6,
                        min_clicks_negate=15, brand_terms=BRAND, junk_words=rulebook.word_list(rulebook.DEFAULT_BLOCK_WORDS))


def by_term(acts):
    out = {}
    for a in acts:
        out.setdefault(a["search_term"], []).append(a["rule"])
    return out


def test_amazon():
    acts = actions_for("amazon_search_terms_sample.csv")
    by = by_term(acts)
    assert by["human body book for kids"] == ["R1 HARVEST", "R1 HARVEST"], by
    assert by["healthy recipes for kids"] == ["R1 HARVEST", "R1 HARVEST"], by
    assert by["science experiments for kids"] == ["R2 NEGATE"]
    assert by["nutrition book for kids"] == ["R2 NEGATE"]
    assert by["science book pdf free download"] == ["R3 JUNK"]
    assert by["free recipe pdf"] == ["R3 JUNK"]
    assert any(a["action"] == "Add NEGATIVE ASIN" for a in acts if a["search_term"] == "b0abc12345")
    assert "dinosaur book for kids" not in by, "1 order is not enough evidence to act"
    assert "sunny shelf book" not in by, "brand searches must never be blocked"
    down = next(a for a in acts if a["rule"] == "R4 BID DOWN")
    assert down["targeting"] == "kids science book" and down["value"] == "₹7.3", down   # 480/46 × 0.7
    up = next(a for a in acts if a["rule"] == "R5 BID UP")
    assert up["targeting"] == "sunny shelf science lab" and up["value"] == "₹3.45", up
    return acts


def test_google():
    rows = rulebook.load(SAMPLES / "google_ads_search_terms_sample.csv")
    assert len(rows) == 5, "title lines skipped and the Total row dropped"
    assert rulebook.norm_match("Exact match (close variant)") == "EXACT"
    acts = actions_for("google_ads_search_terms_sample.csv")
    by = by_term(acts)
    assert by["science kit pdf"] == ["R3 JUNK"]
    assert by["healthy snack ideas kids"] == ["R2 NEGATE"]
    assert "sunny shelf science" not in by
    rules = {(a["targeting"], a["rule"]) for a in acts if a["search_term"] == "(all)"}
    assert ('"science kit"', "R4 BID DOWN") in rules, rules
    assert ("[science kit for kids]", "R4 BID DOWN") in rules
    assert ("[sunny shelf]", "R5 BID UP") in rules
    return acts


def test_cli():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "actions.csv"
        subprocess.run([sys.executable, str(HERE / "rulebook.py"), str(SAMPLES / "amazon_search_terms_sample.csv"),
                        "--brand", "sunny shelf", "--out", str(out)], check=True, capture_output=True, text=True)
        assert len(list(csv.DictReader(open(out, encoding="utf-8")))) == len(test_amazon())


if __name__ == "__main__":
    test_amazon()
    test_google()
    test_cli()
    print("all rule-book tests passed")
