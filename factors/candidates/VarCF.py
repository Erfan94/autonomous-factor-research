"""
VarCF — variance of cash flow to price: the variance over 60 month-ends of
(income before extraordinary items + depreciation) / market equity; high
variability is predicted to earn lower returns.

OSAP: VarCF, Haugen and Baker 1996, Journal of Financial Economics (Table 1
"variability in cf to price"). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/VarCF/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  OSAP: tempCF = (ib + dp) / mve_permco each month; sigma = sample std over a
  trailing 60-month calendar window (current month included, min 24 non-missing);
  VarCF = sigma^2.
  Sharadar, SF1 ART, at each of the 60 business month-ends t-0 .. t-59:
      ib   = SF1.netinc + SF1.netincdis  (PLUS: netincdis carries the OPPOSITE sign to the
             discontinued-operations income it describes, known trap
             sf1_netincdis_sign_inverted; never minus). Not filled: a null netincdis or
             netinc makes that month NaN, as OSAP leaves ib unfilled.
      dp   = SF1.depamor, null -> 0 (OSAP zero-fills dp)
      ME   = SEP.close x SF1.sharesbas at that month-end (price via ctx.at_month_ends
             within 7 days; sharesbas from the latest filing public at that month-end via
             ctx.fundamentals_at_month_ends), as factors/candidates/EP.py. Both are on
             today's split basis; closeunadj is never used. ME > 0 required.
      tempCF_k = (ib + dp) / ME, NaN unless fxusd == 1 at that month-end.
  score = sample variance (ddof = 1) of tempCF_k over the 60 month-ends, a value only
  when ALL 60 month-ends carry a tempCF. The ratio is sign-free: loss-making months
  are kept. ib and dp are TTM flows used as levels, never differenced, so nothing
  smears under ART; dimension ARQ would be 4x too small and is not used.
  Sign: SignalDoc Sign = -1 (high variance earns low returns), so ascending=False.
  OSAP's own portfolio sorts on this signal are monotone with a PLUS sign
  (the SignalDoc Notes; consistent with traditional risk theory) while the Sign
  column carries the paper's minus; the column is the published orientation.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Variance 0 needs a flat
  (ib + dp)/ME series over 60 months; a varying market equity prevents it, so no
  value is a mode. Continuous, heavy right tail (a variance).
  What share of the universe does nothing? Spec measurement (DAILY.marketcap
  denominator, min-24 rule, 253 scored months): modal value 0.052-0.084% of scored
  names (median 0.058%), distinct values equal the scored count (1,194-1,940), ten
  qcut bins in every scored month. This file's window rule differs (see below); the
  distinctness argument is unchanged and preflight measures the rest.
  Tie handling: null. Any month-end without a valid tempCF (missing filing, missing
  price within 7 days, ME <= 0, non-USD) leaves the name NaN, so blend_ranks
  renormalises. Rank, never z-score.

DEVIATIONS FROM OSAP:
  - Full window: all 60 month-ends are required (history_months=59 gates a price at
    t-59, and the factor requires 60 valid observations); OSAP requires 24 of 60.
    The scored sample is therefore narrower than OSAP's and starts later: SEP begins
    1997-12-31, so the first month with a price at t-59 is 2002-11.
  - ART quarterly TTM as known at each month-end (each lag sees only what was public
    then) replaces OSAP's annual Compustat copy stamped datadate + 6 months; the
    variance of a quarterly-stepping series differs from an annual-stepping one.
    Adjacent month-ends share three of four quarters.
  - ib = netinc + netincdis: netinc is after non-controlling interest and
    extraordinary items are not separable from it.
  - ME = SEP.close x SF1.sharesbas (company-level cap, share count steps at filing
    dates, other classes at the primary's price) in place of CRSP mve_permco; the
    price is the last SEP row within 7 days of the month-end.
  - fxusd == 1 gate: the numerator is in the reporting currency over a USD cap.
  - Variance via pandas ddof=1 = polars rolling_std squared; a missing month inside
    the window is a missing observation in OSAP's gap fill and disqualifies the name here.
  - No sample restriction: financials and utilities stay in, as in OSAP.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 60
_LAGS = list(range(_WINDOW))


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    fd = ctx.fundamentals_at_month_ends(["netinc", "netincdis", "depamor", "sharesbas", "fxusd"], _LAGS)
    px = ctx.at_month_ends("SEP", ["close"], _LAGS)
    if fd.empty or px.empty:
        return nan

    key = ["ID", "months_back"]
    m = fd.merge(px[key + ["close"]], on=key, how="inner")
    ib = m["netinc"].astype(float) + m["netincdis"].astype(float)     # netincdis sign inverted: PLUS
    dp = m["depamor"].astype(float).fillna(0.0)                       # OSAP zero-fills dp
    close = m["close"].astype(float)
    sh = m["sharesbas"].astype(float)
    me = (close * sh).where((close > 0) & (sh > 0))
    cf = ((ib + dp) / me).where(m["fxusd"].astype(float) == 1.0)
    m = m.assign(cf=cf.replace([np.inf, -np.inf], np.nan))

    wide = m.pivot_table(index="ID", columns="months_back", values="cf", aggfunc="last")
    n = wide.count(axis=1)
    var = wide.var(axis=1, ddof=1)
    return var.where(n >= _WINDOW).reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="VarCF",
    col="f_varcf",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: HIGH cash-flow variance earns LOWER returns
    weight=1.0,
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.depamor", "SF1.sharesbas", "SF1.fxusd", "SEP.close"),
    osap_acronym="VarCF",
    source="Haugen and Baker 1996 (Journal of Financial Economics)",
    lookback_months=75,             # 60-month window + latest ART filing up to 15 months old at the t-59 end
    history_months=59,              # full 60-month window: a price at t-59
    notes="var(ddof=1) over 60 month-ends of (netinc+netincdis+depamor)/(SEP.close x sharesbas); full window required; ART",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ART)",
         "PLUS (netincdis sign inverted); continuing income after NCI, extraordinary items not separable; not filled; as known at each month-end"),
        ("compustat.dp", "SF1.depamor (ART), null -> 0", "OSAP zero-fills dp"),
        ("crsp.mve_permco", "SEP.close x SF1.sharesbas at each month-end",
         "company-level cap, share count steps at filing dates; both split-restated, never closeunadj; price within 7 days of month-end"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 per month-end"),
        ("rolling_std 60-month window, min_samples 24", "pandas var(ddof=1), all 60 month-ends required",
         "deviation: full window, OSAP's min-24 not reproduced"),
        ("annual Compustat copy at datadate + 6 months", "ART as known at each month-end", "quarterly-refreshing TTM"),
    ),
)
