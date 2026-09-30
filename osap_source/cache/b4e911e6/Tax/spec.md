# Tax — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: DATA_UNAVAILABLE (infeasible): `txfo`, `txfed` and `txdi` have no Sharadar field and OSAP does not zero-fill them
| OSAP input (`m_aCompustat`) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `txfo` (foreign income taxes) | `compustat.txfo` | none | UNAVAILABLE | NOT zero-filled (not in `zero_fill_vars`; no `fillna` in Tax.py): NaN triggers the fallback |
| `txfed` (federal income taxes) | `compustat.txfed` | none | UNAVAILABLE | NOT zero-filled: NaN triggers the fallback |
| `txdi` (deferred income taxes, income statement) | `compustat.txdi` | none | UNAVAILABLE | NOT zero-filled: `txt - txdi` is NaN when txdi is NaN, Tax stays NaN |
| `txt` (total income taxes) | `compustat.txt` | SF1 `taxexp` (ART TTM) | mapped, VENDOR ZERO-FILL (exact 0 on 7.2% of non-null in the universe) | NOT zero-filled (used only in the fallback) |
| `ib` (income before extraordinary items, before preferred dividends) | `compustat.ib` | SF1 `netinc + netincdis` | approx; `sf1_netincdis_sign_inverted`: continuing income = netinc PLUS netincdis (not minus); netinc is after NCI | NaN |
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.
- Missing-item rule: the numerator is `(txfo + txfed)/tr`; if either is missing, OSAP substitutes `(txt - txdi)/tr`. With txfo, txfed AND txdi all unavailable, the
  numerator is NaN for every firm and every `ib > 0` row is dropped (Tax = NaN). None of the three is zero-filled by OSAP, so the rule gives **infeasible**.
- What remains computable: only the rule-3 branches, `Tax = 1.0` when `ib <= 0` (the `Tax.isna() & ib <= 0` branch fires for EVERY ib <= 0 row since the numerator is NaN; `ib == 0`
  with any tax activity likewise). MEASURED on the harness universe, 276 signal months 1998-12-31 .. 2021-11-30 (`build_universe` + `MonthContext.fundamentals`, ART), n mean 1,965:
  | quantity | value |
  |---|---|
  | `ib = netinc + netincdis` non-null | 96.1% of the universe (1,888 names/month) |
  | `ib <= 0` (the only scorable rows) | 18.8% of the universe (mean 369 names; per-month coverage 18.5% mean, 9.0-39.5%); 19.5% of non-null |
  | value taken by every scorable row | 1.0 (single distinct value): mass point = 100% of the scored set |
  | months with coverage >= 40% | 0 of 276 (max 39.5%) |
  | of which `ib <= 0` AND `taxexp > 0` (the true-OSAP "tax paid, loss" mass at 1.0) | mean 153 names = 7.8% of the universe |
  | `taxexp` exact 0 (vendor fill, non-null ART) | 7.2% |
  | `netincdis != 0` | 16.6% of non-null (so ib differs from netinc on one firm in six) |
- A taxexp-only numerator (`taxexp/(tr*ib)`, total tax instead of federal+foreign current tax) is a DIFFERENT signal (includes deferred tax and state tax), not OSAP's Tax; it is not proposed.
  Even then the `ib <= 0 -> 1.0` rule leaves a mass of up to 18.8% of the universe (in the true OSAP, only ib <= 0 with a positive numerator: ~7.8%) at the single value 1.0, above the 10% cliff.
- **Recommendation: `infeasible` (data_unavailable).**

## 2. Variables (exact source names)
`txfo, txfed, ib, txt, txdi` (`m_aCompustat`, $ millions); `permno, time_avail_m`; `year` from `time_avail_m`.

## 3. Formula
```
tr = 0.48 (default);  0.46 for 1979-1986;  0.40 for 1987;  0.34 for 1988-1992;  0.35 for 1993 and later        # year of time_avail_m; per-year scalar, rank-neutral within a month
Tax = ((txfo + txfed) / tr) / ib
where txfo or txfed is NaN:  Tax = ((txt - txdi) / tr) / ib
ib == 0 and any of txfo, txfed, txt, txdi non-null and non-zero:  Tax = 1
Tax NaN and ib <= 0:  Tax = 1                                   # also when ib <= 0 and (txfo+txfed > 0 | txt > txdi | tax activity with both missing)
keep finite Tax
```
Ratio of (estimated) tax-implied taxable income to reported income: > 1 means tax paid exceeds what the book income implies. Output is unbounded (no winsorising); a tiny positive ib gives extreme ratios.

## 4. Timing / lag convention
OSAP: annual Compustat, available 6 months after datadate, replicated for 12 months; one update per year. Harness ART is TTM refreshed quarterly with a ~44-day filing lag, so a mapped
version would update 4x a year and earlier than OSAP. `ib` and `taxexp` are flows (TTM under ART; no year-over-year difference is taken, so no smear under ART). The `tr` year is the month's calendar year.

## 5. Filters
SignalDoc `Filter`: `abs(prc) > 5` (exclude price below 5). The harness universe requires price >= $1 only, so a faithful factor would add a price > 5 condition via `MonthContext` (not a factor-file rule; harness change).

## 6. Predicted sign
`Sign = +1.0` (Lev and Nissim 2004). SignalDoc Notes (OSAP metadata): "Table 5 shows regressions, but it only works in the subsample 1973-1992. Then again Table 6 shows 1993-2000 works as long as you drop 1998. Focuses on forecasting earnings."

## 7. The mass-point question
Two mass points in OSAP's own construction: (a) `ib <= 0` with tax activity -> exactly 1.0 (a do-nothing loss-making firm scores 1); (b) the ratio is continuous otherwise. With the Sharadar inputs only (a) survives,
for all `ib <= 0` firms (18.8% of the universe), and everything else is NaN: a single-valued factor. Tie handling moot (one value, 100% of scored names; preflight hard fail).

## 8. History needed (snapshot starts 1998-01)
No return window; SF1 ART from 1998-01 (first usable month 1998-12 with one TTM filing). Moot given the verdict.

## 9. OSAP metadata
Lev and Nissim (2004), The Accounting Review; Cat.Data Accounting; Cat.Economic other; continuous; sample 1973-2000; Acronym2 Tax2E; Key Table "5A R_TAX"; test "mv reg"; EW;
Portfolio Period 12, Start Month 6; 1_clear / 1_good. SignalDoc Detailed Definition: ratio of taxes paid to tax share of net income; numerator federal + foreign income taxes, else total taxes minus
deferred taxes; denominator tax rate times net income; "if net income is negative, and the numerator is positive, tax is defined as 1". Source `Signals/pyCode/Predictors/Tax.py`; upstream `CompustatAnnual.py` (no zero-fill of txfo, txfed, txdi, txt).

## 10. Proposed Sharadar mappings
None for a faithful Tax. Partial: `ib = netinc + netincdis` (approx), `txt = taxexp` (mapped, vendor zero), `txfo`/`txfed`/`txdi` unavailable (Sharadar has no current/deferred or
federal/foreign tax split; `taxliabilities` is a balance-sheet line, not an income-statement item). Fields not in the map as usable: `compustat.txfo`, `compustat.txfed`, `compustat.txdi` (present in
`field_map_index.yaml`, status unavailable, "infeasible unless OSAP zero-fills it": it does not).
