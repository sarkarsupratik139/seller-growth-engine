# Methodology

The engine is built for the data a small seller actually has: one report a week, a few hundred search terms, and 6–12 weekly data points by the time a decision is due. Every method below says how sure it is, and stays quiet until it has enough data.

## 1. Rule book (R1–R6)

Rules turn search term data into concrete console changes. The browser engine (`app/index.html`) and the Python tool (`engine/rulebook.py`) implement them identically; `tests/engine.test.mjs` checks that both give the same actions on the same reports.

| Rule | Fires when | Action |
|---|---|---|
| **R1 Harvest** | Term from an auto/broad/phrase source has ≥ 2 orders at ACOS ≤ target | Add as an exact keyword at CPC + 10% (capped at max bid); add as a negative exact in the source |
| **R2 Negate** | 0 orders after ≥ *N* clicks (default 15), or spend ≥ 1.5 × (price × target ACOS) | Negative exact (or negative ASIN for a product target) |
| **R3 Junk** | Term contains a blocked word as a whole word | Negative phrase on that word |
| **R4 Bid down** | Keyword ACOS > 1.3 × target, ≥ 2 orders | Bid = CPC × max(0.7, target ÷ ACOS), floor 1 |
| **R5 Bid up** | Keyword ACOS < 0.7 × target, ≥ 2 orders | Bid +15%, capped |
| **R6 Starved** | Exact keyword with < 100 impressions | Bid +20%, capped |

Guardrails:
- Brand words are never blocked.
- Bids never drop more than 30% a week, and never rise above the max bid.
- Each product's own price sets its thresholds.
- With 7-day reports, the rules see the last 14 days, because the engine adds last week's saved rows.

## 2. Statistics and machine learning

| Business question | Method | Starts at | Why it fits |
|---|---|---|---|
| Will we pass at week 8? | OLS regression of weekly units on week number; forecast at week 8 with an **80% prediction interval** (Student *t*) | 3 weeks | The interval widens with few or noisy weeks. The outlook says "PASS likely" only when even the low end clears the +50% line. |
| Do ads add sales, or just capture them? | Multiple regression: units = *a* + *b* × ad spend + *c* × week. *b* is the ad effect with the trend held fixed, and counts only if it is significant at 95% | 6 weeks (a simple read from 4) | Separates the effect of ads from growth that would have happened anyway. If spend and time move together (\|r\| ≥ 0.9), or spend varies < 10%, it reports that the effect can't be measured and recommends a budget test. |
| Which search terms behave alike? | k-means on standardised log-clicks, CTR, conversion and capped ACOS; *k* from 3–5 chosen by the best **silhouette**; deterministic farthest-point start | 6 terms with ≥ 3 clicks | Groups are named from their averages (Winners, Money drains, Costly converters…). Each name comes with an action. The same data always gives the same groups. |
| Is a term quietly wasting money? | Binomial test: P(0 orders in *n* clicks \| account conversion rate) | 2 weeks | Flags a "slow bleeder" only when that chance is < 10% and spend is meaningful. Normal bad luck isn't punished. |
| Is this week unusual? | The latest week against the **95% prediction interval** of the earlier weeks' trend, in the bad direction only, and ≥ 20% off | 5 weeks | Comparing to the trend, not the average, stops normal growth looking like an alarm. |
| Are ads eating organic sales? | Trend slopes of ad-driven and organic units; flagged only if both are significant (80%) and in opposite directions | 4 weeks | Avoids false alarms on noise. |

**Overlapping reports.** Weekly runs on 14-day reports share 7 days, so weekly points aren't independent. The engine then:
- treats *n* weeks as *n* × 7 ÷ days independent points, for degrees of freedom;
- widens every standard error by √(days ÷ 7);
- says so in the findings.

Use 7-day reports to avoid this.

**Weekly equivalents.** Totals from reports of any length are converted to per-week figures before any trend is fitted.

**Sample isolation.** Demo weeks are left out of every calculation as soon as one real week exists.

**Verification** (`tests/engine.test.mjs`):
- regression recovers an exact line;
- multiple regression recovers known coefficients;
- k-means and silhouette separate obvious clusters;
- the demo history produces forecasts and a decision;
- sample weeks are excluded.

## 3. The decision engine

One budget call per week; the first matching row wins.

| # | Condition | Call |
|---|---|---|
| 1 | ACOS above blended break-even | **Cut 20%** |
| 2 | Profit after ads negative and ACOS above target | **Cut 10%** |
| 3 | Ad effect proven (95%) and ad cost per extra unit < profit per unit | **Raise 20%** |
| 4 | ACOS under target but the ad effect is unproven or unmeasurable | **Budget test +30% for 2 weeks** |
| 5 | ACOS under target, ad effect not testable yet | **Raise 15%** |
| 6 | ACOS between target and break-even | **Hold** |

Priorities follow, each with a ₹ impact per week:
1. **Cut waste:** block search terms from R2/R3 and slow bleeders; shows the spend saved.
2. **Grow:** move proven searches to exact match (R1); shows the orders they already bring.
3. **Efficiency:** lower bids above target (R4).
4. **Grow:** raise bids (R5/R6); push rising search terms.
5. **Listing:** when conversion drops, winners fade, or organic sales fall while ad sales rise.

## 4. The AI layer

The language model sits **on top of** the deterministic engine, never in place of it:
- **What it receives:** the computed summary, the decision, the priorities, the findings and the forecasts, as JSON.
- **What it is told:** use only those numbers, copy them exactly, and never compute or invent figures.
- **What it produces:** a short plain-language brief with a headline, what happened, the decision, actions and one risk.

This keeps the numbers auditable and makes the output explainable to a store owner. The [roadmap](ROADMAP.md) extends this to drafted actions and guarded automation.

## 5. Known limits

- **Linear trends only:** seasonality and festivals are not modelled yet.
- **Ad attribution windows** (7 days on Amazon) credit some sales that would have happened anyway.
- **The rules use fixed thresholds** suited to small accounts; larger accounts may need tuning.
- **The ad-effect test is observational.** A deliberate budget test is stronger evidence, which is why the engine recommends one when the evidence is unclear.
