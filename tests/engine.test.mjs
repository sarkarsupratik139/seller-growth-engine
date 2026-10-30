// Tests for the browser engine in app/index.html (no dependencies):
//   node tests/engine.test.mjs
// Checks the parsers, the statistics, the decision logic, and that the browser rules
// give exactly the same actions as engine/rulebook.py on the same sample reports.
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = fs.readFileSync(path.join(root, "app/index.html"), "utf8");
const engine = html.match(/<script id="engine">([\s\S]*?)<\/script>/)[1];
const E = new Function(engine + "; return { mapTable, normRow, runRules, buildRun, analyze, decide, demoRuns, reportPeriod, parseBusinessReport, linreg, ols, kmeans, silhouette, wordList, DEFAULT_BLOCK_WORDS };")();

let passed = 0;
const test = (name, fn) => { fn(); passed++; console.log("ok -", name); };

// minimal CSV reader for the samples (quoted fields, doubled quotes)
function readCSV(file) {
  const text = fs.readFileSync(path.join(root, "sample-data", file), "utf8").replace(/^﻿/, "");
  const out = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n") { row.push(cell); out.push(row); row = []; cell = ""; }
    else if (c !== "\r") cell += c;
  }
  if (cell || row.length) { row.push(cell); out.push(row); }
  return out;
}

const BRAND = "sunny shelf, sunnyshelf";
const settings = { periodDays: 7, targetAcos: 30, dailyBudget: 500, maxBid: 15, currentBid: 6, minClicks: 15, brandWords: BRAND, blockWords: E.DEFAULT_BLOCK_WORDS };
const products = [
  { name: "Junior Science Lab Book", match: "science", asin: "B0DEMO0001", price: 399, cogs: 120, referral: 45, fba: 65, baseline: 10, periodUnits: 15, periodSales: 5985 },
  { name: "Snack Smart Cookbook", match: "snack", asin: "B0DEMO0002", price: 349, cogs: 100, referral: 40, fba: 60, baseline: 5, periodUnits: 6, periodSales: 2094 },
];
const jsActions = file => E.runRules(E.mapTable(readCSV(file)).map(E.normRow),
  { price: 399, targetAcos: 0.3, maxBid: 15, currentBid: 6, minClicksNegate: 15, brandTerms: E.wordList(BRAND), junkWords: E.wordList(E.DEFAULT_BLOCK_WORDS) });

test("Google Ads export: title lines skipped, Total row dropped, match types normalised", () => {
  const rows = E.mapTable(readCSV("google_ads_search_terms_sample.csv")).map(E.normRow);
  assert.equal(rows.length, 5);
  assert.equal(rows.find(r => r.term === "science kit for 10 year old").match, "EXACT");
  assert.equal(rows.find(r => r.term === "kids science lab kit").spend, 1050);
});

test("Amazon export: report period read from its dates", () => {
  const p = E.reportPeriod(E.mapTable(readCSV("amazon_search_terms_sample.csv")));
  assert.deepEqual([p.start, p.end, p.days], ["2026-10-19", "2026-10-25", 7]);
});

test("Business Report: units and sales per product by ASIN, others ignored", () => {
  const t = readCSV("business_report_sample.csv");
  const { per, unmatched } = E.parseBusinessReport(t[0], t.slice(1), products);
  assert.deepEqual(per.map(p => [p.units, p.sales]), [[15, 5985], [6, 2094]]);
  assert.equal(unmatched.length, 1);
});

for (const file of ["amazon_search_terms_sample.csv", "google_ads_search_terms_sample.csv"]) {
  test(`browser rules match engine/rulebook.py exactly (${file})`, () => {
    const py = JSON.parse(execFileSync("python3", ["-c",
      `import json,sys; sys.path.insert(0,'engine'); import rulebook as r
a=r.run(r.load('sample-data/${file}'),399,0.30,15,6,15,r.word_list(${JSON.stringify(BRAND)}),r.word_list(r.DEFAULT_BLOCK_WORDS))
print(json.dumps([[x['rule'],x['action'],x['value'],x['search_term']] for x in a]))`], { cwd: root, encoding: "utf8" }));
    const js = jsActions(file).map(a => [a.rule, a.action, a.value, a.search_term]);
    const key = a => a.join("|");
    assert.deepEqual(js.map(key).sort(), py.map(key).sort());
    assert.ok(js.length >= 5);
  });
}

test("brand searches are never blocked", () => {
  const terms = jsActions("amazon_search_terms_sample.csv").filter(a => /^R[23]/.test(a.rule)).map(a => a.search_term);
  assert.ok(!terms.some(t => t.includes("sunny shelf")));
});

test("linear regression recovers an exact line", () => {
  const f = E.linreg([0, 1, 2, 3], [1, 3, 5, 7]);
  assert.ok(Math.abs(f.slope - 2) < 1e-12 && f.r2 > 0.9999);
});

test("multiple regression recovers known coefficients", () => {
  const X = [[1, 1, 0], [1, 2, 1], [1, 0, 2], [1, 3, 3], [1, 1, 4], [1, 4, 5]];
  const y = X.map(r => 2 + 3 * r[1] + 0.5 * r[2]);
  const f = E.ols(X, y);
  assert.ok(Math.abs(f.beta[1] - 3) < 1e-6 && Math.abs(f.beta[2] - 0.5) < 1e-6);
});

test("k-means + silhouette separate two obvious groups", () => {
  const X = [[0, 0], [0.1, 0], [0, 0.1], [5, 5], [5.1, 5], [5, 5.1]];
  const { assign } = E.kmeans(X, 2);
  assert.equal(new Set(assign.slice(0, 3)).size, 1);
  assert.notEqual(assign[0], assign[3]);
  assert.ok(E.silhouette(X, assign) > 0.9);
});

test("demo history: forecasts, decision and priorities are produced", () => {
  const runs = E.demoRuns(products, settings, "2026-10-19");
  assert.equal(runs.length, 6);
  const A = E.analyze(runs), D = E.decide(runs.at(-1), A);
  assert.ok(A.trends[0].projected > 0 && A.trends[0].low <= A.trends[0].projected);
  assert.ok(["Raise", "Cut", "Hold", "Test"].includes(D.call));
  assert.ok(D.items.length > 0);
});

test("sample weeks are left out once a real week exists", () => {
  const runs = E.demoRuns(products, settings, "2026-10-19");
  const real = { ...runs.at(-1), sample: false, week: "2026-10-26" };
  const A = E.analyze([...runs, real]);
  assert.equal(A.n, 1);
  assert.equal(A.hiddenSample, 6);
});

console.log(`\n${passed} tests passed`);
