# Architecture

## Design choices

| Choice | Why |
|---|---|
| **One self-contained HTML file** | A small seller can run it by double-clicking. No install, no server, no account, nothing to maintain. |
| **Deterministic engine, AI on top** | Every number is reproducible and testable. The LLM explains and, later, drafts actions; it never computes. |
| **Browser storage** | Store data never leaves the device. IndexedDB holds the weekly history; localStorage holds settings. |
| **Same rules in JS and Python** | The page is for people; `engine/rulebook.py` is for scripts and future automation. A parity test keeps them identical. |
| **Statistics before complexity** | With 6–12 weekly points, interpretable methods with honest intervals beat black-box models. |

## Code map (`app/index.html`)

The page has two script blocks.

**`<script id="engine">`**: pure functions with no DOM access, loaded by the Node tests.

| Area | Functions |
|---|---|
| Parsing | `mapTable` / `mapColumns` (header detection, Amazon and Google aliases), `parseDate`, `reportPeriod`, `parseBusinessReport`, `normRow`, `normMatch` |
| Rules | `runRules` (R1–R6) |
| Weekly run | `buildRun`: rules, totals, per-product economics, organic units, profit after ads |
| Statistics / ML | `linreg` (with prediction error), `ols`, `invert`, `corr`, `kmeans`, `silhouette`, `aggregateTerms` |
| Analysis | `analyze`: trends and forecasts, ad-spend effect, profit and organic trends, term patterns, clusters, alerts, findings |
| Decisions | `decide`: budget call and priorities; `verdict`: 8-week test |
| Demo | `demoRuns`: seeded, reproducible 6-week sample history |

**Second script**: the user interface, with the same layout in the page:
- the weekly-history database (`DB`), with a memory fallback;
- product setup and settings;
- report import (CSV parser, SheetJS for XLSX);
- the run, results and decision box;
- the AI brief;
- history, insights and SVG charts;
- the Excel report (ExcelJS, chart images rendered from the on-screen SVG).

## Data model

```
Run (one per week, key = Monday's date)
├── week, source, sample, savedAt, period {start, end, days}
├── settings      target ACOS, budget, bids, brand and blocked words
├── products[]    name, campaign word, ASIN, price, costs, fees, baseline, units and sales in period
├── rows[]        normalised search-term rows
├── actions[]     rule, action, value, campaign, targeting, term, clicks, spend, orders, ACOS, why
├── byProduct[]   spend, sales, orders, weekly units, organic, profit after ads
└── summary       totals, ACOS, TACoS, weekly units, baseline, break-even, organic, profit after ads
```

A backup file is `{ version, products, entered, settings, runs[] }`.

## AI integration

The **Write AI brief** button calls the Anthropic Messages API from the browser:
- **Request:** `POST https://api.anthropic.com/v1/messages` with `anthropic-version: 2026-10-21` and the browser-access header.
- **Content:** a fixed system prompt plus a JSON payload of the computed results.
- **Models:** Claude Opus 5.5 by default; Sonnet 5.5 and Haiku 5.5 are selectable.
- **Settings:** effort `low` (it's a short summary).
- **Refusals:** on Opus and Sonnet, the server-side refusal fallback is enabled (`anthropic-beta: server-side-fallback-2026-07-01`, `fallbacks: "default"`). A `refusal` stop reason is reported to the user.
- **Excel:** the brief is added to the Excel dashboard for that week.

On the roadmap, this call moves behind a small hosted proxy, so keys stay server-side and usage can be capped per store.

## External dependencies

| Library | Used for | Loaded |
|---|---|---|
| SheetJS 0.18.5 (cdnjs) | Reading XLSX reports | On page load |
| ExcelJS 4.4.0 (jsDelivr) | Writing the Excel report | On first export |

CSV input, rules, statistics, charts and history all work offline.
