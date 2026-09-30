"""
NetPayoutYield — net payout to shareholders (dividends plus repurchases minus issuance)
over the company's market value six months earlier. High net payers are expected to earn
higher returns.

OSAP: NetPayoutYield, Boudoukh, Michaely, Richardson, Roberts 2007, Journal of Finance
(Table 6D). Predicted sign: + (SignalDoc Sign = +1), so ascending=True (HIGH raw is the
attractive / long leg).
Spec: osap_source/cache/b4e911e6/NetPayoutYield/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  predictor.py: (dvc + prstkc - sstk) / mve_permco lagged 6 months.
  ART (trailing four quarters) latest filing known at the BME(t-6) month-end, via ctx.fundamentals_at_month_ends(["ncfcommon",
  "ncfdiv","fxusd","equity","sharesbas"], [6]); a flow can be up to ~21 months old at t:
      num = -(ncfdiv.clip(upper=0) + ncfcommon.fillna(0)),  NaN where ncfdiv is null
  Sign conventions (verified against osap_source/field_map.yaml, sstk and dv/dvc entries):
    ncfdiv = cash dividends paid, OUTFLOW-NEGATIVE, so dvc == -ncfdiv (a positive ncfdiv,
      0.19% of rows, wrong sign, is clipped to 0).
    ncfcommon = NET common-equity flow, INFLOW-positive, so prstkc - sstk == -ncfcommon.
    Hence dvc + prstkc - sstk == -(ncfdiv + ncfcommon): a net payer is positive.
  Zero-fills follow OSAP: sstk and prstkc are zero-filled (null ncfcommon -> 0); dvc is
  NOT zero-filled (only dvt is), so a null ncfdiv gives NaN.
  ME_t-6 = SEP.close x SF1.sharesbas, both at the business month-end six months before the
  signal, built as EP builds it: price via ctx.at_month_end("SEP", ["close"], 6), share
  count via ctx.fundamentals_at_month_ends(["sharesbas"], [6]) (latest filing public at
  that month-end). sharesbas is split-restated to today's basis and SEP.close is on the
  same basis, so the product is consistent; never paired with closeunadj. Scaled to
  dollars against the reporting-currency flows (both in units of USD; sharesbas is a
  count, close is USD per share).
  score = num / ME_t-6   (ME_t-6 > 0 guarded, close > 0 and sharesbas > 0).
  Raw ratio, no log, no winsorising.

OSAP'S OWN SAMPLE SCREENS, reproduced inside the signal (NaN output, not a universe
change; as GP does for financials):
  - Net payout exactly 0 -> NaN (OSAP removes the row). Null-flow non-payers (ncfcommon
    null -> 0 with ncfdiv == 0) fall into the same removal, consistent with OSAP's
    zero-fill of sstk/prstkc. The 1e-19 float-residual OSAP keeps when components are
    nonzero but cancel is not reproduced (exact zeros are nulled).
  - Financials: SIC 6000-6999 -> NaN (OSAP keeps sic < 6000 or sic >= 7000), read through
    ctx.ticker_meta(["siccode"]). That SIC is TODAY's vendor classification, not the code
    in force in the month scored (known trap current_sic_signal_values): a look-ahead of
    the same kind the sector ranking carries (DECISIONS D3). A null SIC is NaN, as in
    OSAP (NaN fails both sides of the test).
  - ceq <= 0 -> NaN (OSAP keeps ceq > 0 or missing), read as SF1.equity, which includes
    preferred, so the screen is nearly immaterial.
  - fxusd != 1 -> NaN: a reporting-currency flow over a USD cap (<= 0.06% of members).
  - history_months=24 stands for OSAP's obs_count >= 24 (at least 24 observations after
    the other filters). A factor may not filter the universe; the harness history gate
    requires a price 24 months back. This counts listing age, not filtered firm-months.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0 (no dividend, no buyback, no
  issuance). OSAP REMOVES it, as does this file (score != 0).
  What share of the universe does nothing? Spec measurement on the 264 scorable months:
  exact zeros are 1.0-4.2% of names with data (median 2.0%), nulled by the rule; the
  modal value of the scored set is 0.055-0.082% (2-3 names), distinct values equal scored
  n (minimum 1,220). Preflight re-measures it on this mapping.
  Tie handling: remove (as OSAP; exact zero -> NaN, so blend_ranks renormalises). Net
  issuers are negative and net payers positive: a two-sided continuous tail.

DEVIATIONS FROM OSAP:
  - ncfcommon EXCLUDES preferred issuance/redemption (Compustat prstkc/sstk include it);
    the TARP-era error is muted because SIC 6xxx is dropped.
  - ncfdiv is predominantly common-only (matches dvc), but combined-line filers add
    preferred, and it is cash paid rather than declared.
  - mve_permco -> SEP.close x SF1.sharesbas at the t-6 month-end (company-level cap;
    share count steps at filing dates). The t-6 price is read within 7 calendar days of
    the month-end.
  - Timing: OSAP takes annual flows at datadate + 6 months, held 12 months, with ME at t-6
    (the fiscal year-end month). Here the flows (and equity, fxusd) are the latest ART
    filing known at the BME(t-6) month-end (one fundamentals_at_month_ends call with sharesbas, refreshed quarterly), so
    the t-6 price is at or after the end of the flow window, as in OSAP and as EP does
    (alpha_review batch08 medium on EP's unlagged timing). The flow is a TTM LEVEL
    over a price level: no year-over-year difference, nothing to smear, no dimension
    override.
  - ceq -> SF1.equity (includes preferred); SIC is the current classification.
  - The 24-observation count is replaced by history_months=24 (listing age). DAILY is not
    read; SEP starts 1997-12, so the first scorable signal is 1999-12-31 (the first 12
    decision months are null by construction).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    # flows, equity, currency and shares as known at the BME(t-6) month-end, one call, so the
    # t-6 price follows the flow window (as EP); a flow can be up to ~21 months old at t
    fa = ctx.fundamentals_at_month_ends(["ncfcommon", "ncfdiv", "fxusd", "equity", "sharesbas"], [6])
    if fa.empty:
        return pd.Series(np.nan, index=ctx.ids)
    f = fa[fa["months_back"] == 6].drop_duplicates("ID", keep="last").set_index("ID").reindex(ctx.ids)

    ncfdiv = f["ncfdiv"].astype(float)
    # dvc + prstkc - sstk = -(ncfdiv<=0 part + ncfcommon); ncfcommon zero-filled, ncfdiv not
    num = -(ncfdiv.clip(upper=0.0) + f["ncfcommon"].astype(float).fillna(0.0))
    num = num.where(ncfdiv.notna())

    # market equity six months earlier, built as EP builds it
    p6 = ctx.at_month_end("SEP", ["close"], 6)
    sh6 = f["sharesbas"].astype(float)
    c6 = p6["close"].astype(float).reindex(ctx.ids)
    me6 = (c6 * sh6).where((c6 > 0) & (sh6 > 0))

    score = (num / me6).replace([np.inf, -np.inf], np.nan)

    score = score.where(f["fxusd"].astype(float) == 1.0)       # reporting currency vs USD cap
    score = score.where(score != 0)                            # OSAP: exact-zero net payout removed

    eq = f["equity"].astype(float)
    score = score.where(eq.isna() | (eq > 0))                  # OSAP: ceq > 0 or missing kept

    # OSAP sample screen: financials by CURRENT SIC (look-ahead, declared); null SIC -> NaN
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce").reindex(ctx.ids)
    nonfin = sic.notna() & ~((sic >= 6000) & (sic < 7000))
    return score.where(nonfin)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="NetPayoutYield",
    col="f_npy",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high net payout yield is the long leg
    weight=1.0,
    inputs=("SF1.ncfcommon", "SF1.ncfdiv", "SF1.fxusd", "SF1.equity", "SF1.sharesbas",
            "SEP.close", "TICKERS.siccode"),
    osap_acronym="NetPayoutYield",
    source="Boudoukh, Michaely, Richardson, Roberts 2007 (Journal of Finance)",
    lookback_months=24,             # 24-month history gate; ME read 6 months back
    history_months=24,              # stands for OSAP's obs_count >= 24 (listing age, declared)
    notes=("-(min(ncfdiv,0) + ncfcommon.fillna(0)) / (SEP.close x sharesbas at t-6), ART; exact 0 -> NaN; "
           "SIC 6000-6999 (current) / ceq<=0 / fxusd!=1 -> NaN; null ncfdiv -> NaN"),
    field_mappings=(
        ("dvc", "-SF1.ncfdiv.clip(upper=0)",
         "outflow-negative sign flipped; predominantly common-only (combined-line filers add preferred; cash paid vs declared); null -> NaN (dvc not zero-filled); positive 0.19% clipped"),
        ("prstkc - sstk (zero-filled)", "-SF1.ncfcommon.fillna(0)",
         "NET common flow, inflow-positive; PREFERRED EXCLUDED (Compustat includes it); null -> 0 as OSAP zero-fill"),
        ("crsp.mve_permco at t-6", "SEP.close x SF1.sharesbas at the t-6 month-end",
         "as EP: company-level cap, share count steps at filing dates; split-restated pair, never closeunadj; > 0 guarded"),
        ("net payout == 0 removed", "score.where(score != 0)", "exact zero -> NaN as OSAP; the 1e-19 residual patch is not reproduced"),
        ("sic 6000-6999 dropped", "TICKERS.siccode (current)", "look-ahead current classification (known trap current_sic_signal_values); sample screen only; null SIC -> NaN as OSAP"),
        ("ceq > 0 or missing", "SF1.equity", "includes preferred, so nearly immaterial"),
        ("curcd", "SF1.fxusd", "gate fxusd == 1"),
        ("obs_count >= 24", "history_months=24", "listing age, not filtered firm-months"),
        ("time_avail_m", "SF1.datekey (ART)", "TTM flows at filing, quarterly refresh; 6-month ME lag kept from OSAP; no 6-month annual lag on flows"),
    ),
)
