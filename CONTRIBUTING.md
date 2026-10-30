# Contributing

Thanks for helping small sellers grow.

## Ground rules

- **Numbers stay deterministic.** Rules and statistics live in the `<script id="engine">` block of `app/index.html`, as pure functions with no DOM access. AI features may explain or draft, never compute.
- **Keep the rule book in sync.** Any change to R1–R6 goes into both `app/index.html` and `engine/rulebook.py`. The parity test must pass.
- **No real store data** in issues, tests or samples. Use the fictional *Sunny Shelf* data in `sample-data/`.
- **One file, no build step** for the app. New libraries come from a pinned CDN version and are loaded only when needed.

## Before opening a pull request

```bash
python3 engine/test_rulebook.py
node tests/engine.test.mjs
```

Then open `app/index.html`, load the demo history, run a week, and download the Excel report.

## Good first issues

- Blocked-word presets for a product category
- An importer for another marketplace's search-term report
- More tests for edge cases (empty reports, a single week, all-zero spend)
