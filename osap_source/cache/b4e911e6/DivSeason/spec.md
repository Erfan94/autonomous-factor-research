# DivSeason — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX on data (ACTIONS dividends; `cd1/cd2/cd3` not reproducible); PREFLIGHT-FAIL as a screen (binary, mode 71.5-78.7% of the scored cross-section)
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP `divamt`, `exdt` (`CRSPdistributions`) | `ACTIONS.value`, `action == 'dividend'`; `date` = ex-date | field_map `crsp.divamt` approx. AAPL 2014 check: ACTIONS values are on today's split basis (AAPL 2014-02..11 value 0.1175 x 28 (7:1 in 2014 and 4:1 in 2020) = 3.29 as paid, the same factor as SEP close/closeunadj); irrelevant to a paid/not-paid flag |
| `cd1 == 1 & cd2 == 2` (regular cash dividend) | none | NOT reproducible: ACTIONS carries cash dividends only, incl. specials. Not OSAP-zero-filled; approx by the DivInit/DivOmit judgement (owner may rule infeasible) |
| `cd3` (frequency code: 0/1 unknown, 2 monthly, 3 quarterly, 4 semi-annual, 5 annual, 6+ other) | none | NOT reproducible. The signal branches on it three ways and drops cd3 == 2 and >= 6. Only approximation: treat every payer as quarterly (OSAP's own rule for unknown/missing frequency, 0/1) or infer frequency from ACTIONS payment gaps (an invention; not OSAP) |
| `permno, time_avail_m` (SignalMasterTable) | SEP presence x universe | harness-side |
- Panel rule (as DivInit spec section 1): paid = presence of an ACTIONS dividend row for a universe member, absence = did not pay; build universe x ACTIONS, never ACTIONS alone. 54% of dividend rows have no ID (non-universe names); for universe names "paid in 12m" agrees with SF1 `dps > 0` on 98.1-99.9% of dps-known names.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`CRSPdistributions`: permno, cd1, cd2, cd3, divamt, exdt. `SignalMasterTable`: permno, time_avail_m. `asrol` (calendar-month rolling sum), `stata_ineq_pd`.

## 3. Formula
```
keep cd1==1 & cd2==2; time_avail_m = month(exdt); sum divamt by (permno, cd3, month); keep first cd3 per permno-month (sorted)
df = SignalMasterTable left-join; drop rows before the firm's first dividend record; cd3 = ffill; divamt NaN -> 0
divpaid = divamt > 0;  drop cd3 == 2 (monthly);  keep cd3 < 6   (NaN cd3 also fails `< 6`: never-paid firms drop out)
divpaid_sum = rolling 12-month sum of divpaid (t-11..t);  DivSeason = 0 if divpaid_sum > 0 else NaN
temp3 = cd3 in (0,1,3) & any(divpaid.shift(2,5,8,11) > 0)     # quarterly / unknown
temp4 = cd3 == 4 & any(divpaid.shift(5,11) > 0)                # semi-annual
temp5 = cd3 == 5 & divpaid.shift(11) > 0                       # annual
DivSeason = 1 if temp3 | temp4 | temp5
```
Values: 1 = a dividend is predicted for next month (paid 3/6/9/12 months before it), 0 = paid within 12 months but not predicted next month, NaN = no dividend in the last 12 months. Non-payers are NaN, not 0. `shift(n)` is ROW-based in OSAP (a calendar gap makes it miss); the harness version uses calendar months.

## 4. Timing / lag
OSAP: event month = month of ex-date, signal dated t used for month t+1. Harness: ACTIONS `date <= signal_asof`; `ctx.actions("dividend", months_back)` windows by DateOffset on the month-end, so aggregate to calendar months on `date`. The month-t ex-date (known at declaration, 2-4 weeks before) is usable. No SF1, so no ART/ARQ issue and no flow smear.

## 5. Filters
SignalDoc Filter `abs(prc) > 5`: harness universe has price >= $1 only, so penny-$1-5 names are scored here (deviation; a factor may not filter). Common-stock restriction is the harness universe.

## 6. Predicted sign
`Sign = +1.0` (Hartzmark-Solomon 2013 Table 2B, t = 16.19, 0.36%/month): stocks predicted to pay a dividend next month earn more, relative to other payers. `ascending=True`. Direction is within the payer set; NaN non-payers take no part.

## 7. Mass-point question
Do-nothing firm: a payer with no payment at lags 2/5/8/11 gets 0; a non-payer is NaN. Measured on the universe month by month (46 of the 276 decision months, every 6th, 1998-12 .. 2021-06 signals; quarterly-for-all approximation of cd3):
- scored coverage (paid in 12m): 35.4% (2000-06) .. 62.3% (2016-12) of the universe, median ~52%; scored names 798-1,160 per month.
- value 0: 71.5-78.7% of the scored names (635-894 names); value 1: 21.3-28.5% (220-295 names). Shares of the WHOLE universe: 1 = 8.8-15.3%, 0 = 26-48%, NaN (non-payers) = 38-65%.
- Preflight hard fails: mode >= 10% (71.5-78.7%) and 2 distinct values so `qcut` yields 2 bins, not 10. The measured verdict is preflight-fail in every probe month; it cannot be rescued by tie handling (a binary signal has no within-group order).
- Tie handling if an owner overrides: average rank, IC is point-biserial; Stage 1 deciles and D10-D1 are undefined (two buckets); the >= 30 names per decile floor is met (220+) but the decile count is not.
- The ~25% ones is below the 33% a clean quarterly panel gives because of ex-date drift across month boundaries and non-quarterly payers.

## 8. History needed (snapshot starts 1998-01; ACTIONS 1997-12 is a 19-row stub)
Window t-11..t (12 months) plus `shift(11)`: first fully covered signal month 1998-12 (ACTIONS 1998-01..1998-12), which IS the first decision-month signal (1999-01). All **276** of 276 decision months have a defined signal (for payers). `lookback_months` = 12; no `history_months` (no return window).

## 9. OSAP metadata
Hartzmark and Solomon (2013), JFE; Cat.Data Event; Cat.Economic payout indicator; Cat.Form discrete; sample 1927-2011; Acronym2 DivSeason; Test "LS port", Key Table 2B long (1) short (2); Portfolio Period 1, Start Month 12; EW; 1_clear / 1_good; Filter `abs(prc)>5`. Source `Signals/pyCode/Predictors/DivSeason.py`.

## 10. Proposed Sharadar mappings (only if the owner overrides the preflight verdict)
`paid_m` = any `ACTIONS` dividend row (`0 < value <= 10*SEP.close`) for (ID, calendar month of `date`) via `ctx.actions("dividend", 12)` (universe x ACTIONS; cap vendor outliers as in DivInit). `DivSeason = 0` if paid in t-11..t else NaN; `= 1` if paid in any of t-2, t-5, t-8, t-11 (quarterly for every name). Declare `ACTIONS.value`, `ACTIONS.action`; `lookback_months=12`; `ascending=True`.
Deviations: `cd1/cd2` filter absent (specials included); `cd3` absent (all names quarterly: monthly payers, which OSAP drops, are scored; semi-annual/annual payers are over-flagged 1 at lags 2/8 and 2/5/8); no `abs(prc) > 5`; calendar-month vs row-based shifts. Fields in map: `crsp.divamt` (approx); `cd1/cd2/cd3` have no map entry (unavailable).
