# HerfBE — Industry concentration (book equity) (Hou and Robinson 2006, Table 2 H(Equity))

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/HerfBE.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor):
Cat.Data = Other, Cat.Economic = other, Predictability 1_clear, Signal Rep Quality 1_good.

## 1. Data availability (verdict: APPROX — preferred term missing; preflight expected to pass on the cross-section)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `seq` (first choice for equity) | `compustat.seq` | SF1.equity | mapped | one unsplit equity line incl. preferred; null 0.05% |
| `ceq`, `at`, `lt` (fallbacks) | `ceq` / `at` / `lt` | SF1.equity / assets / liabilities | approx / mapped / mapped | fallback branch immaterial (equity null 0.05%) |
| `pstk`, `pstkrv`, `pstkl` (preferred, subtracted) | `compustat.pstk*` | none | unavailable | book_equity_preferred_terms ruling: only adjusts BE -> approx |
| `txditc` (`fillna(0)`, added) | `compustat.txditc` | SF1.taxliabilities.fillna(0) | approx | generic tax-liability line; Sharadar zero-fills 51% itself |
| `sicCRSP`, `shrcd` | `crsp.siccd`, `crsp.shrcd` | TICKERS.siccode (CURRENT), TICKERS.category | approx | as HerfAsset |
| SignalMasterTable row | `crsp.smt_row` | SEP presence, market scope | mapped | industry sums over all listed common stock |

- Nothing structural is unavailable. Preferred stock only adjusts book equity (seq + txditc - pstk), so per the
  ruling (2026-09-25) the predictor is `approx`: BE = `equity + taxliabilities.fillna(0)`, preferred NOT removed.
  Stated deviation; a firm with large preferred is overstated in its industry's equity. Current SIC as HerfAsset.
- Recommendation: `approx`, proceed.

## 2. Variables (exact source names)

`permno`, `time_avail_m`, `txditc`, `pstk`, `pstkrv`, `pstkl`, `seq`, `ceq`, `at`, `lt` (m_aCompustat);
`sicCRSP`, `shrcd` (SignalMasterTable); `utils.asrol`.

## 3. Formula

```
txditc = txditc.fillna(0); tempPS = pstk.fillna(pstkrv).fillna(pstkl)
tempSE = seq.fillna(ceq + tempPS).fillna(at - lt)
tempBE = tempSE + txditc - tempPS                                  # book equity, NO floor, may be negative
sic3D  = str(sicCRSP)[:4]                                          # 4-digit despite the name
indequity = groupby([sic3D,time_avail_m])["tempBE"].sum();  tempHerf = sum of (tempBE/indequity)**2 in group
HerfBE = asrol(permno, 36 months, mean of tempHerf, min_samples=12); NaN if shrcd>11; regulated-industry NaN
         (4011/4210/4213 <=1980; 4512 <=1978; 4812/4813 <=1982; any 49xx)
```
- Same four-digit grouping as HerfAsset (SignalDoc says "three digit"; pinned code keeps four): use
  `harness.industry.sic_group(sic, 4)`. Merge `how="inner"`; `drop_duplicates(permno,time_avail_m)` first.
- **No floor on negative BE, reproduce, do not fix.** An industry whose summed BE is small or negative, or a
  negative-BE firm, makes a share outside [0,1] and H > 1 (no upper bound). Measured on the scored universe rows:
  H > 1 on 2.3% of rows on average (ART; ARY 2.2%), max 5.3% of a month (4.8% ARY), e.g. 5.3% at 2021-11. These
  rank at the top; it is a tail, not a mass point.
- Only the 49xx rule is live in 1999-2021; 49xx is 5.0% of the universe (3.6-6.2%).

## 4. Timing / lag

As HerfAsset: OSAP annual data lagged 6 months from datadate; the harness reads the latest filing by datekey (ART,
max age 15 months) at each of 36 lagged business month-ends via
`fundamentals_at_month_ends(["equity","taxliabilities"], range(36), scope="market")`, keeping a firm at a lag only if
it traded that month. Levels, no TTM smear; recommend ART (ARY gives 89.7% vs 91.0% mean coverage). Signal stamped
at month-end m, earns m+1. Needs >= 12 observed months: first scorable signal month 1998-12.

## 5. Filters

Common stock (universe); 49xx excluded; null SIC NaN (0.0% in the universe). No price or size rule.

## 6. Predicted sign

SignalDoc `Sign = -1.0`: Hou-Robinson Table 3 H(Equity), characteristics-adjusted portfolio sort, EW, t = 2.52,
return 0.24; Portfolio Period 1, Start Month 6; sample 1963-2001; "Judgment call". `ascending=False`.

## 7. The mass-point question

As HerfAsset the value is an industry attribute, so SIC4 firms with the same history tie exactly. Measured on the
harness universe (`build_universe`, all 276 signal months 1998-12-31..2021-11-30):
- Scored share (siccode, not 49xx, >= 12 observed months): ART mean 91.0%, ARY 89.7% (same scored set as HerfAsset);
  1998-12 48.1% ART / 44.0% ARY, 1999-01 55.7% / 44.8%, from 1999-02 >= 80.6% / 75.4%; 0 months under 40%;
  scored n median 1,745 (ART), min 1,097.
- Cross-section mode share: median 5.9%, max 7.7% (ART), 0 of 276 months at or above 10%; 10 `qcut` bins always;
  distinct values median 430 (ART). Modal block is SIC 6798 (REITs), 94 / 111 / 136 names at 2008-12 / 2013-12 /
  2021-11 (ART; the modal value differs from HerfAsset's since BE, not assets, weights the firms).
- **Within sector (the D3 ranking), ART run, modal-value share at 2008-12 / 2013-12 / 2021-11: Real Estate
  92% / 86% / 82%, Energy 44% / 42% / 39%, Healthcare 26% / 30% / 29%, Technology 18-22%, Financial Services
  18-21%, Communication Services 13-23%, others under 10%; Utilities 1-2 names.** The D3 sector rank removes
  most variation in Real Estate and Energy. Flag, not a verdict; preflight reads the cross-section and passes.
- Tie handling: average rank. Do-nothing value: a lone firm in its SIC4 gives exactly 1.0 (about 0.9% of scored).

## 8. History needed

OSAP sample 1963-2001. Snapshot SF1 starts 1997Q4, SEP 1997-12: the 36-month window is full from about 2001-01,
first scorable signal month 1998-12 (12-observation minimum). `lookback_months` ~ 51 (36 + 15). No `history_months`.

## 9. OSAP metadata

Acronym HerfBE, Hou and Robinson 2006, Journal of Finance, "Industry concentration (equity)". Cat.Form
continuous, Cat.Data Other, Cat.Economic other, Quantile 0.2 EW, Key Table in OP `2 H(Equity)`, test "port sort
char adjusted", GScholar cites 1316. Output column `HerfBE`.

## 10. Proposed Sharadar mappings

| OSAP | Sharadar | deviation |
|---|---|---|
| tempBE = seq(+fallbacks) + txditc - tempPS | SF1.equity + SF1.taxliabilities.fillna(0) (ART) | preferred not removed (ruling); taxliabilities generic; equity fallback chain dropped (0.05%) |
| `sicCRSP` -> 4-digit group | TICKERS.siccode via `sic_group(.,4)`, market scope | CURRENT SIC, look-ahead in the value (D3 kind) |
| SMT / m_aCompustat row | listed at lag AND filing <= 15m old | as HerfAsset |
| industry sum over all CRSP-Compustat | `ctx.market_context()` market scope | same set, vendor coverage |
| `asrol` 36m, min 12 | mean of per-month H over lags 0..35, n >= 12 | as HerfAsset |
| regulated-industry NaN | 49xx only | current SIC |

Guard: do not floor or clip BE; nulls only where `equity` is null. Orientation `ascending=False`. Fields not in the
field map index: none.
