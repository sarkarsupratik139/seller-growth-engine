# Growth playbook

This is the strategy the engine is built to run. It is written for a small seller with a few products, a modest ad budget (around ₹500 a day) and no agency. The demo store, *Sunny Shelf*, is fictional.

## Principle: success is total sales, not ad clicks

Ads are judged on whether **total** units grow against a pre-ads baseline, at an ad cost the margin can carry. A campaign with great ad metrics that only moves sales from organic to paid is a failure.

**The 8-week test:**
- **PASS:** units up at least 50% on the baseline, with TACoS at or below 25%.
- **ITERATE:** units up 20–49%.
- **FAIL:** units up less than 20%.

## Step 0 · Fix the listing before buying traffic (week 0)

Ads can't fix a page that doesn't convert. Before spending:
- complete titles, bullets and descriptions with the words shoppers search for;
- add 6–7 images, including a size and contents shot, plus A+ content where available;
- collect reviews through the marketplace's own programmes. Under 15 ratings makes conversion the main bottleneck;
- check price against the 3 closest competitors;
- make sure the product is in stock with fast delivery (e.g. FBA), and holds the Buy Box.

## Step 1 · Know the unit economics

| Line | Example (₹) |
|---|---|
| Price | 399 |
| − Cost per unit | 120 |
| − Marketplace referral fee | 45 |
| − Fulfilment fee | 65 |
| **= Profit per unit before ads** | **169** |
| **Break-even ACOS** = 169 ÷ 399 | **42%** |
| Target ACOS (stay safely below) | 30% |
| Max ad cost per order = 399 × 30% | 120 |

The engine calculates this for every product and warns you if the target ACOS would lose money.

## Step 2 · Campaign structure (Amazon Sponsored Products example)

Name every campaign with the product's word so the engine can link it, e.g. "SP | Auto | Science".

| Campaign | Share of ₹500/day | Purpose |
|---|---|---|
| Auto · main product | 25% | Discover search terms |
| Broad / phrase · main product | 20% | Controlled discovery on chosen themes |
| Exact winners | 20% | Proven terms moved here by rule R1 |
| Product targeting · competitors | 15% | Appear on competing product pages |
| Brand defence (exact) | 10% | Own your brand searches cheaply |
| Auto · second product | 10% | Discovery for the second product |

For Google Ads search, use the same shape: a discovery campaign (broad/phrase), an exact-winners campaign, and a brand campaign. The rules apply unchanged to its search terms report.

## Step 3 · The weekly loop (every Monday)

1. Download the search term report and the Business Report for the last 7 days.
2. Run the engine.
3. Apply the changes.
4. Read the decision.
5. Send the report.

The [user guide](USER_GUIDE.md) has the details. In the console itself, set once:
- budget rules (raise budget when ROAS is high);
- seasonal and event boosts;
- top-of-search bids for brand defence;
- dayparting, if your sales cluster in certain hours.

## Step 4 · The 90-day plan

| Weeks | Focus | Output |
|---|---|---|
| 0 | Listing fixes, baseline measured, campaigns built | Baseline units per week; campaigns live |
| 1–2 | Discovery: auto and broad collect search terms | First negatives and harvested winners |
| 3–4 | Efficiency: bids toward target ACOS, waste blocked | ACOS trending to target |
| 4–6 | Budget test if the ad effect is unclear | Clean read on whether ads add sales |
| 6–8 | Scale what works | Week-8 verdict: PASS / ITERATE / FAIL |
| 9–12 | Scale (PASS), fix listing and keywords (ITERATE), or pause and fix the product (FAIL) | Next 90-day plan |

## Step 5 · Multiple touch points

Marketplace ads are one channel. Small sellers also have cheap, high-intent touch points:

| Touch point | Example | How to track its effect on marketplace sales |
|---|---|---|
| Google Ads (search) | Brand and category searches | Search terms report into the engine; a marketplace attribution tag where available |
| Social (Instagram, Facebook) | Short videos, creators | One coupon code or tagged link per channel |
| Offline events | School fairs, community events | A QR code to the listing with its own tag; event-week bump vs trend |
| Professional referrals | Doctors, teachers, trainers recommending the product | A referral code per partner |
| Email / WhatsApp | Existing customers | A campaign code; sales in the send week |

Rule of thumb: every channel gets a budget, one tracking method and one weekly KPI. Tracking these inside the engine is on the [roadmap](ROADMAP.md).
