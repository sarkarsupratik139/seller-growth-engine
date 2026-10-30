# User guide

Seller Growth Engine turns two weekly reports into a budget decision, a list of console changes, an 8-week scorecard and an Excel report. A weekly run takes about 10 minutes.

## 1. The weekly routine

Use **7-day reports**. They don't overlap from week to week, which keeps the trend statistics clean. The engine adds last week's saved data automatically, so the rules still judge 14 days of data.

1. **Search term report**
   - *Amazon:* Ads console → Measurement & Reporting → Sponsored reports → *Sponsored Products · Search term · Summary · Last 7 days* → download.
   - *Google Ads:* Insights and reports → Search terms → last 7 days → download as CSV.
2. **Total sales**
   - *Amazon:* Seller Central → Reports → Business Reports → *Detail Page Sales and Traffic by Child Item*, same 7 days → download CSV.
   - *Elsewhere:* type the units and sales per product into step 2b.
3. Open `app/index.html` in Chrome or Edge. Drop file 1 on **2a** and file 2 on **2b**. The week and period are filled in from the report's dates.
4. Click **Run Monday check**. The week is saved automatically. Sample data is not saved unless you choose to save it.
5. Read the **decision box**: the budget call, then the numbered priorities.
6. Make the changes from the **Actions** table in the ads console.
7. Optionally click **Write AI brief**.
8. Click **Download Excel report** and share it.
9. Once a month: **Back up all data** and keep the .json file safe.

First time only:
- fill in **Product setup** with real costs and fees, and the baseline units per week from the 4 weeks before ads started;
- set your **brand words** and **blocked words**.

## 2. Screen by screen

Yellow cells are your data. Orange italics mark a placeholder estimate that still needs a real figure.

### 1 · Product setup (once)

| Field | Meaning | Where to find it |
|---|---|---|
| Product | Display name | — |
| Campaign name contains | Word that links an ad campaign to this product, e.g. `science` matches "SP \| Auto \| Science" | Your campaign naming |
| ASIN | Links Business Report rows to the product | Marketplace listing |
| Price, Cost per unit, Referral fee, FBA fee (₹) | Unit economics, used for profit per unit and break-even ACOS | Marketplace fee preview; supplier invoice |
| Baseline units/week | Average weekly units in the 4 weeks before ads | Sales report |
| Profit/unit, Break-even ACOS, Max ad cost/order | Calculated. A ⚠ appears if the target ACOS would lose money | — |

**Rule settings:**

| Setting | Default | What it does |
|---|---|---|
| Report period | set from the report | Days the report covers |
| Target ACOS | 30% | Highest ad cost per ad sale you'll accept |
| Current daily budget | ₹500 | Basis for the budget recommendation |
| Max bid | ₹15 | Highest bid the engine will ever suggest |
| Default bid | ₹6 | Bid assumed for keywords with no clicks |
| Clicks before blocking | 15 | Clicks with no sale before a search is blocked |
| Brand words | — | Searches containing these are never blocked |
| Blocked words | free, pdf, download, used, second hand, torrent, jobs | Searches containing these get a negative phrase |

### 2 · This week's data

- **2a Search term report:** drop the Amazon or Google Ads file. Rows can be checked and edited under *Show / edit rows*. *Load sample data* fills in demo rows.
- **2b Business Report:** drop the file and units and sales per product fill in, or type them. These are **total** sales (ads plus organic) for the same dates.

### 3 · Run

*Week of* is set from the report. *Run Monday check* builds and saves the week. It warns you if the sales figures are unchanged from last week or are still placeholders.

### 4 · Decision and actions

- **Decision box:** the budget call (Raise / Cut / Hold / Budget test), the new daily budget, the reason, and the priorities with ₹ impact per week.
- **AI brief (optional):** paste an Anthropic API key, pick a model and click *Write AI brief*. No key? *Copy prompt instead* and paste it into any AI chat.
- **Tiles:**
  - ad spend per week, ad sales, ACOS, TACoS
  - units per week, of which organic
  - profit after ads per week
  - number of changes to make
- **By-product table**, then the **action list**, which you can filter by rule.
- **Downloads:** Excel report and actions.csv.

### 5 · History · 8-week scorecard

- One row per week, with missing weeks flagged.
- The PASS / ITERATE / FAIL verdict.
- Buttons: *Load 6-week demo history*, *Back up* / *Restore*, *Delete sample weeks*, *Delete all*.

### 6 · Trends · insights

Findings in plain English, then:
- three charts: units against the pass line with the week-8 range, profit after ads, and units from ads vs organic;
- the forecast table;
- the search-term groups;
- the search-term patterns.

## 3. The 8-week test

The engine judges success on **total units**, not ad clicks. At week 8:

| Verdict | Condition |
|---|---|
| **PASS** | Units ≥ +50% on the baseline, and TACoS (ad spend ÷ all sales) ≤ 25% |
| **ITERATE** | Units +20–49% |
| **FAIL** | Units under +20% |

Week 1 is the first real saved week. Demo weeks never count.

## 4. The Excel report

| Sheet | Contents |
|---|---|
| **Dashboard** | Decision, 8 KPI tiles, priorities with ₹ impact, 3 charts, findings, AI brief (if written), by-product table |
| **Actions** | Every console change, colour-coded by rule, with a *Done?* dropdown |
| **Search terms** | This week's terms with CTR, CPC, conversion, ACOS (shaded green to red) and ML group |
| **Weekly history** | One row per week: spend, ACOS, TACoS, units from ads vs organic, profit after ads, units per product |
| **Forecast & ML** | Week-8 forecasts with ranges, ad-spend effect test, k-means groups with silhouette score, alerts |
| **Term patterns** | Slow bleeders, rising, fading and consistent winners, with what to do |
| **Inputs** | Product economics and settings used that week |

Building the report needs an internet connection the first time, to load the Excel library.

## 5. Data and privacy

- **Where data is kept:** all data stays in the browser where the page is opened. History is in the browser's database; settings are in local storage.
- **Another browser or computer** starts empty. Use *Back up all data* and *Restore backup* to move data.
- **Clearing browsing data** for local files erases the history, so back up first.
- **Re-running a week** replaces that week.
- **The AI brief** sends a summary of the week's numbers (not the raw reports) to the Anthropic API using your key. Use a key with a spending limit.

## 6. Glossary

| Term | Meaning |
|---|---|
| ACOS | Ad spend ÷ sales from ads |
| TACoS | Ad spend ÷ all sales (ads + organic): shows whether ads grow the whole business |
| Break-even ACOS | Profit per unit before ads ÷ price; above it every ad sale loses money |
| Max ad cost per order | Price × target ACOS |
| CPC / CTR / CVR | Cost per click / clicks ÷ impressions / orders ÷ clicks |
| Organic units | Total units minus ad orders |
| Profit after ads | Units × profit per unit − ad spend, per week |
| Harvest | Moving a proven search term into its own exact-match keyword |
| Negative exact / phrase | Stops ads for that exact search / any search containing the phrase |
| 80% range | Where the week-8 value lands 4 times out of 5 if the trend holds |

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| "Missing column for '…'" | Wrong report type. Re-download the search term report (Amazon: *Summary* time unit). |
| "No rows found for <product>" | That product's ASIN or campaign word in step 1 doesn't match the Business Report. |
| A campaign shows as "Not linked to a product" | Its name doesn't contain any product's *Campaign name contains* word. |
| Warning that sales are unchanged | Step 2b still holds last week's figures. |
| Excel or XLSX input needs internet | The libraries load from a CDN the first time; CSV input always works offline. |
| History empty on another computer | History is per browser; use *Restore backup*. |
| AI brief error 401 | The API key is wrong or revoked. |
| "Need N more weeks" | Forecasts start at 3 real weeks, the ad-effect test at 6. |
