"""Seller Growth Engine: the weekly ads rule book as a command-line tool.

Reads a search term report and writes the list of changes to make in the ads console.
Accepted inputs (CSV or XLSX):
  * Amazon Ads: Sponsored Products > Search term report (summary)
  * Google Ads: Search terms report

    python3 rulebook.py search_terms.csv --price 399 --target-acos 0.30 --brand "sunny shelf"

Rules (same IDs, thresholds and output as the browser app in app/index.html):
    R1 HARVEST   converting search term -> add as exact keyword, negate in source
    R2 NEGATE    clicks or spend with no orders -> negative exact
    R3 JUNK      blocked words (free, pdf, ...) -> negative phrase
    R4 BID DOWN  ACOS above the target band -> lower bid toward target
    R5 BID UP    ACOS well below target -> raise bid
    R6 STARVED   exact keyword with too few impressions -> raise bid
Brand searches are never blocked.
"""
import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

# Column names accepted from Amazon and Google Ads exports (first match wins, case-insensitive).
COLS = {
    "campaign": ["Campaign Name", "Campaign"],
    "ad_group": ["Ad Group Name", "Ad group"],
    "targeting": ["Targeting", "Keyword"],
    "match": ["Match Type"],
    "term": ["Customer Search Term", "Search Term"],
    "impr": ["Impressions", "Impr."],
    "clicks": ["Clicks"],
    "spend": ["Spend", "Spend(INR)", "Spend (INR)", "Spend (₹)", "Cost"],
    "sales": ["7 Day Total Sales", "7 Day Total Sales (₹)", "7 Day Total Sales (INR)", "14 Day Total Sales",
              "14 Day Total Sales (₹)", "Conv. value", "Total conv. value", "Sales"],
    "orders": ["7 Day Total Orders (#)", "7 Day Total Orders", "14 Day Total Orders (#)", "Conversions", "Orders"],
}
DEFAULT_BLOCK_WORDS = "free, pdf, download, used, second hand, torrent, jobs"


def word_list(s):
    return [w.strip().lower() for w in str(s or "").split(",") if w.strip()]


def map_header(header):
    """Index of each needed column in this header row, or None if one is missing."""
    h = [str(x or "").strip().lower() for x in header]
    idx = {}
    for key, names in COLS.items():
        found = next((h.index(n.lower()) for n in names if n.lower() in h), None)
        if found is None:
            return None
        idx[key] = found
    return idx


def load(path):
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        from openpyxl import load_workbook
        table = [list(r) for r in load_workbook(p, read_only=True, data_only=True).active.iter_rows(values_only=True)]
    else:
        with open(p, newline="", encoding="utf-8-sig") as f:
            table = list(csv.reader(f))
    # exports can start with title or date-range lines: the header is the first row with every needed column
    for i, row in enumerate(table[:10]):
        idx = map_header(row)
        if idx:
            rows = [{k: (r[j] if j < len(r) else "") for k, j in idx.items()} for r in table[i + 1:] if any(c not in ("", None) for c in r)]
            is_total = lambda v: re.match(r"^total\b", str(v or "").strip(), re.I)
            return [r for r in rows if not is_total(r["campaign"]) and not is_total(r["term"])]
    sys.exit(f"No header row with all of: {', '.join(n[0] for n in COLS.values())}")


def num(x):
    if x is None or x == "":
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    try:
        return float(re.sub(r"[₹$€£,%]", "", str(x)).strip() or 0)
    except ValueError:
        return 0.0


def norm_match(m):
    """'Exact match (close variant)' (Google) and 'EXACT' (Amazon) -> 'EXACT'."""
    return re.sub(r"\bMATCH\b", "", re.sub(r"\(.*?\)", "", str(m or "").upper())).strip()


def aggregate(rows):
    """Sum per (campaign, ad group, targeting, match, term) in case the export is daily."""
    agg = defaultdict(lambda: {"impr": 0, "clicks": 0, "spend": 0.0, "sales": 0.0, "orders": 0})
    for r in rows:
        k = (r["campaign"], r["ad_group"], r["targeting"], norm_match(r["match"]), str(r["term"]).strip().lower())
        a = agg[k]
        for f in ("impr", "clicks", "orders"):
            a[f] += int(num(r[f]))
        a["spend"] += num(r["spend"])
        a["sales"] += num(r["sales"])
    return agg


def is_asin(term):
    return len(term) == 10 and term.startswith("b0")


def fmt_bid(x):
    """Format like the browser app: 7.3 not 7.30, 6 not 6.0."""
    return f"{x:.2f}".rstrip("0").rstrip(".")


def run(rows, price, target_acos, max_bid, current_bid, min_clicks_negate, brand_terms=(), junk_words=None):
    junk_words = word_list(DEFAULT_BLOCK_WORDS) if junk_words is None else junk_words
    target_cpa = price * target_acos
    actions, exact_terms = [], set()
    by_target = defaultdict(lambda: {"impr": 0, "clicks": 0, "spend": 0.0, "sales": 0.0, "orders": 0, "match": ""})
    agg = aggregate(rows)

    for (camp, ag, targeting, match, term), a in agg.items():
        if match == "EXACT":
            exact_terms.add(term)
        t = by_target[(camp, ag, targeting)]
        for f in ("impr", "clicks", "spend", "sales", "orders"):
            t[f] += a[f]
        t["match"] = match

    for (camp, ag, targeting, match, term), a in sorted(agg.items(), key=lambda kv: -kv[1]["spend"]):
        acos = a["spend"] / a["sales"] if a["sales"] else None
        base = dict(campaign=camp, ad_group=ag, targeting=targeting, search_term=term,
                    clicks=a["clicks"], spend=round(a["spend"], 2), orders=a["orders"],
                    acos=f"{acos:.0%}" if acos is not None else "—")
        is_brand = any(b in term for b in brand_terms)

        # R3 blocked words: negative phrase, regardless of data volume
        root = next((j for j in junk_words if re.search(rf"\b{re.escape(j)}\b", term)), None)
        if root and not is_brand:
            actions.append({**base, "rule": "R3 JUNK", "action": "Add NEGATIVE PHRASE",
                            "value": root, "why": f"contains '{root}', not a buyer of a ₹{price:.0f} product"})
            continue

        # R1 harvest: converting term from auto/broad/phrase -> exact
        if match != "EXACT" and a["orders"] >= 2 and acos is not None and acos <= target_acos and term not in exact_terms:
            kind = "ASIN target" if is_asin(term) else "EXACT keyword"
            bid = min(max_bid, round(a["spend"] / max(a["clicks"], 1) * 1.1, 2))
            actions.append({**base, "rule": "R1 HARVEST", "action": f"Add as {kind} in 'SP | Exact winners'",
                            "value": f"bid ₹{fmt_bid(bid)}", "why": f"{a['orders']} orders at {acos:.0%} ACOS ≤ target {target_acos:.0%}"})
            actions.append({**base, "rule": "R1 HARVEST", "action": "Add NEGATIVE EXACT in source ad group",
                            "value": term, "why": "stop the source campaign competing with the exact campaign"})
            continue

        # R2 negate bleeders (never brand terms)
        if a["orders"] == 0 and not is_brand and (a["clicks"] >= min_clicks_negate or a["spend"] >= 1.5 * target_cpa):
            kind = "NEGATIVE ASIN" if is_asin(term) else "NEGATIVE EXACT"
            actions.append({**base, "rule": "R2 NEGATE", "action": f"Add {kind}", "value": term,
                            "why": f"{a['clicks']} clicks / ₹{a['spend']:.0f} spent, 0 orders "
                                   f"(limit {min_clicks_negate} clicks or ₹{1.5 * target_cpa:.0f})"})

    # keyword-level bid rules (auto groups are managed through negatives, not bids)
    for (camp, ag, targeting), t in by_target.items():
        if targeting in ("*", "") or t["match"] in ("-", ""):
            continue
        acos = t["spend"] / t["sales"] if t["sales"] else None
        cpc = t["spend"] / t["clicks"] if t["clicks"] else current_bid
        base = dict(campaign=camp, ad_group=ag, targeting=targeting, search_term="(all)",
                    clicks=t["clicks"], spend=round(t["spend"], 2), orders=t["orders"],
                    acos=f"{acos:.0%}" if acos is not None else "—")
        if t["orders"] >= 2 and acos is not None and acos > target_acos * 1.3:
            new = max(1.0, round(cpc * max(0.7, target_acos / acos), 2))
            actions.append({**base, "rule": "R4 BID DOWN", "action": "Set bid", "value": f"₹{fmt_bid(new)}",
                            "why": f"ACOS {acos:.0%} > {target_acos * 1.3:.0%}; max cut 30% per week"})
        elif t["orders"] >= 2 and acos is not None and acos < target_acos * 0.7:
            new = min(max_bid, round(cpc * 1.15, 2))
            actions.append({**base, "rule": "R5 BID UP", "action": "Set bid", "value": f"₹{fmt_bid(new)}",
                            "why": f"ACOS {acos:.0%} < {target_acos * 0.7:.0%}; buy more of a winner (+15%)"})
        elif t["match"] == "EXACT" and t["impr"] < 100:
            new = min(max_bid, round(max(cpc, current_bid) * 1.2, 2))
            actions.append({**base, "rule": "R6 STARVED", "action": "Set bid", "value": f"₹{fmt_bid(new)}",
                            "why": f"only {t['impr']} impressions this period; bid too low to enter auction (+20%)"})
    return actions


FIELDS = ["rule", "action", "value", "campaign", "ad_group", "targeting", "search_term",
          "clicks", "spend", "orders", "acos", "why"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="search term report (CSV or XLSX)")
    ap.add_argument("--price", type=float, default=399, help="selling price per unit")
    ap.add_argument("--target-acos", type=float, default=0.30, help="target ad cost ÷ ad sales, e.g. 0.30")
    ap.add_argument("--max-bid", type=float, default=15, help="highest bid ever suggested")
    ap.add_argument("--current-bid", type=float, default=6, help="bid assumed when a keyword got no clicks")
    ap.add_argument("--min-clicks-negate", type=int, default=15, help="clicks with no sale before blocking")
    ap.add_argument("--brand", default="", help="comma-separated brand words that are never blocked")
    ap.add_argument("--block", default=DEFAULT_BLOCK_WORDS, help="comma-separated words that mark a non-buyer search")
    ap.add_argument("--out", default="actions.csv")
    args = ap.parse_args()

    actions = run(load(args.report), args.price, args.target_acos, args.max_bid, args.current_bid,
                  args.min_clicks_negate, word_list(args.brand), word_list(args.block))
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(actions)
    counts = defaultdict(int)
    for a in actions:
        counts[a["rule"]] += 1
    print(f"{len(actions)} actions -> {args.out}")
    for r in sorted(counts):
        print(f"  {r}: {counts[r]}")
    print(f"(target cost per order ₹{args.price * args.target_acos:.0f}; block after {args.min_clicks_negate} clicks "
          f"or ₹{math.ceil(1.5 * args.price * args.target_acos)} with no order)")


if __name__ == "__main__":
    main()
