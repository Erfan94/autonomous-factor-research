"""
DelDRC — 12-month change in deferred revenue over average total assets, for
non-financial, positive-equity, non-trivial-revenue firms whose deferred
revenue actually moved (a rising deferred-revenue balance = contracted,
not-yet-recognised sales).

OSAP: DelDRC (Acronym2 DeferRev), Prakash & Sinha 2013, Contemporary
Accounting Research. Predicted sign: + (SignalDoc Sign = +1, ascending=True).
Spec: osap_source/cache/b4e911e6/DelDRC/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["deferredrev","assets","equity","revenue","fxusd"])
  (ART default; latest filing known at the signal and the same fiscal period
  one year earlier, aligned by reportperiod). Deferred revenue is a balance
  (level), so the ART yoy change is a clean 12-month change.
    drc    = deferredrev, null -> 0 where that period's filing exists
    avgAT  = 0.5 * (assets + assets_lag), guarded > 0
    DelDRC = (drc - drc_lag) / avgAT
  Missing year-ago filing, or assets / assets_lag null -> NaN.

SAMPLE RESTRICTIONS INSIDE THE SIGNAL (OSAP's own definition; NaN output, not a
universe change). Each uses NaN-false semantics as OSAP does: a missing input
does NOT trigger the exclusion.
  - equity <= 0 -> NaN (ceq <= 0).
  - revenue < $5 million -> NaN (Compustat sale < 5 is in $ millions; Sharadar
    is raw USD). The latest ART revenue is converted to USD (revenue / fxusd)
    before the test; the ratio itself is currency-free. Null revenue is kept.
  - SIC 6000-6999 -> NaN, read through ctx.ticker_meta(["siccode"]). That SIC is
    TODAY's vendor classification, not the code in force in the month scored:
    a look-ahead of the same kind the sector ranking carries (DECISIONS D3
    kind). A missing SIC is not treated as financial.
  - deferred revenue zero at BOTH ends: drc == 0 and the change == 0 -> NaN
    (OSAP: (drc == 0) & (DelDRC == 0)). Zero now with a non-zero year-ago level
    (or the reverse) stays scored.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no deferred
  revenue now or a year ago).
  What share of the universe does nothing? Large before the restriction:
  roughly 63-72% of names carry zero deferred revenue at both ends (Sharadar
  zero-fills the field). After the restriction the survivors with an exact-zero
  change (drc > 0, unchanged) are a fraction of 1% per the spec's measurement;
  preflight measures the modal-value share on the harness universe.
  Tie handling: REMOVE (restrict the sample). The zero-at-both-ends names are
  set NaN inside the signal, which is OSAP's own filter and coincides with the
  standing tie rule, so no mass point is left and the harness's average rank
  covers any residual ties. COST: coverage is structurally thin (spec measured
  roughly 20-27% non-null on raw SF1 before the harness universe); the filter
  is implemented faithfully and NOT weakened to raise coverage. A coverage
  shortfall against the 40% floor is a preflight measurement, not a defect
  here.

DEVIATIONS FROM OSAP:
  - drc -> deferredrev: Sharadar deferredrev is TOTAL deferred revenue
    (current + non-current = Compustat drc + drlt); OSAP uses the current
    portion drc only. Firms with only long-term deferred revenue score here and
    are zero (hence removed) in OSAP. Used once, not added to anything.
  - ceq -> equity: parent equity incl. preferred; the screen tests only the sign.
  - SIC is current, not point-in-time (see above).
  - Timing: OSAP reads the fiscal year available at datadate + 6 months,
    refreshed annually; here the latest filed ART level against the same
    period a year earlier (rolling four-quarter change, refreshed quarterly),
    no 6-month lag.
  - revenue is an ART trailing-four-quarter flow used only as a level screen;
    in 1998 it is ~50% populated, and null revenue is not excluded.
  - OSAP's price / NYSE-breakpoint filters are the harness universe's, not
    reproduced.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["deferredrev", "assets", "equity", "revenue", "fxusd"])
    have_now = y["reportperiod"].notna()
    have_ago = y["reportperiod_lag"].notna()

    # OSAP zero-fills drc: null -> 0 only where that period's filing exists.
    drc = y["deferredrev"].astype(float)
    drc = drc.where(~(have_now & drc.isna()), 0.0)
    drc_lag = y["deferredrev_lag"].astype(float)
    drc_lag = drc_lag.where(~(have_ago & drc_lag.isna()), 0.0)

    at = y["assets"].astype(float)
    at_lag = y["assets_lag"].astype(float)
    den = 0.5 * (at + at_lag)
    chg = drc - drc_lag
    score = chg / den.where(den > 0)
    score = score.where(have_now & have_ago)

    # OSAP filters as NaN in the signal. NaN-false: a missing input never excludes.
    equity_bad = y["equity"].astype(float) <= 0
    fx = y["fxusd"].astype(float)
    rev_usd = y["revenue"].astype(float) / fx.where(fx > 0)
    rev_small = rev_usd < 5e6
    zero_both = (drc == 0) & (chg == 0)
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")
    sic = sic.reindex(score.index)
    financial = (sic >= 6000) & (sic < 7000)
    drop = equity_bad | rev_small | zero_both | financial
    return score.where(~drop).replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelDRC",
    col="f_deldrc",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH change in deferred revenue is attractive
    weight=1.0,
    inputs=("SF1.deferredrev", "SF1.assets", "SF1.equity", "SF1.revenue", "SF1.fxusd",
            "TICKERS.siccode"),
    osap_acronym="DelDRC",
    source="Prakash & Sinha 2013 (Contemporary Accounting Research)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes=("(drc - drc_yearago) / avg assets; ART yoy by reportperiod; NaN if equity<=0, revenue<$5m, "
           "current SIC 6000-6999, or drc==0 at both ends; total (not current) deferred revenue"),
    field_mappings=(
        ("compustat.drc", "SF1.deferredrev (ART)",
         "APPROX: TOTAL deferred revenue (drc + drlt), OSAP uses the current portion; null -> 0 where filing exists (OSAP zero-fills)"),
        ("compustat.at", "SF1.assets (ART)", "avg of latest and year-ago, guarded > 0"),
        ("compustat.ceq", "SF1.equity (ART)", "filter ceq <= 0 -> NaN; equity includes preferred (immaterial); null not excluded (NaN-false)"),
        ("compustat.sale", "SF1.revenue / fxusd (ART TTM)",
         "filter sale < 5 ($m) -> revenue_usd < 5e6; null not excluded (NaN-false); flow used as a level screen only"),
        ("compustat.sic", "TICKERS.siccode",
         "CURRENT classification (look-ahead, D3 kind); SIC 6000-6999 -> NaN; missing SIC kept"),
        ("(drc == 0) & (DelDRC == 0) filter", "same, on SF1 levels",
         "zero deferred revenue at both ends -> NaN (removes the mass point; coverage structurally ~20-27% before the harness universe)"),
        ("drc.shift(12)", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance), not a 12-row shift; missing/stale -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
