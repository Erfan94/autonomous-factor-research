"""
RoE — return on equity: net income over book equity, how much after-tax profit a
unit of shareholder capital earns.

OSAP: RoE, Haugen and Baker 1996, Journal of Financial Economics ("Commonality in
the determinants of expected stock returns", Table 1, return on equity).
Predicted sign: + (high RoE earns higher returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/RoE/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ni  = SF1.netinc   (ART, trailing-twelve-month, latest filing known at the signal)
  ceq = SF1.equity   (ART, same filing)
  score = ni / ceq.where(ceq > 0)
  Raw ratio, no log, no winsorising. ascending=True (SignalDoc Sign = +1).
  Numerator is Compustat `ni` (parent net income after non-controlling interest,
  before preferred dividends, including discontinued operations), which is SF1.netinc;
  the `ib = netinc + netincdis` trap does not apply because OSAP reads `ni`, not `ib`.
  Both fields are in reporting currency so the ratio is currency-free: no fxusd gate
  and no market term.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - equity <= 0 -> NaN. OSAP has no guard: a negative book gives a sign-flipped
    ratio (a loss-maker scores positive) and a zero book gives +/-inf, which its
    dropna does not drop. Here those names are nulled (3.2% of equity-non-null names
    in the spec's sample, range 1.7%-6.9%).
  - Non-finite results -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None: the ratio is continuous and
  has no constant. The only exact-0 case is netinc == 0 to the dollar.
  What share of the universe does nothing? Spec measurement on 92 of 276 decision
  months: modal share 0.06% mean (max 0.12%); distinct values == n; exact ni == 0 is
  0.01% of non-null names (max 0.09%); 10 qcut bins. Preflight measures it again.
  Tie handling: null (equity <= 0 guard); no rule otherwise. |RoE| > 5 (tiny positive
  equity) is 0.5% of scored names (max 1.2%); OSAP does not trim and neither does this.

OVERLAP WITH THE v0 COMPOSITE (factual):
  The Profitability leg is (revenue - cor - (sgna + rnd + intexp)) / equity (ART,
  equity > 0). RoE has the SAME denominator (SF1.equity, same filing); the numerators
  differ (operating profit before tax versus after-tax net income to the parent).
  Spec-measured cross-sectional Spearman of raw RoE with the raw Profitability leg:
  mean 0.71 (range 0.62-0.81, 92 months).

DEVIATIONS FROM OSAP:
  - ni: fiscal-year annual `ni` available datadate + 6 months and held 12 months ->
    SF1.netinc ART (TTM as of the latest filing, no extra 6-month lag). Different
    information horizon, same concept.
  - ceq -> SF1.equity, which INCLUDES preferred stock (OSAP ceq excludes it; SF1 has
    no pstk). RoE is slightly understated for preferred issuers (ruling
    book_equity_preferred_terms: approx).
  - equity <= 0 -> NaN (OSAP keeps the sign-flipped / infinite rows).
  - dimension ART (the default): ARQ would put one quarter of income over equity.
  - OSAP's annual-row requirement (at, prcc_c, ni non-missing), the abs(prc) > 5
    filter and duplicate-keep-first are not reproduced (universe belongs to the
    harness; one SF1 row per ID as-of).
  - Coverage: ART netinc is ~57% populated for reportperiod 1998, so the first
    decision month is thin; >= 83% from 1999.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["netinc", "equity"])
    ni = f["netinc"].astype(float)
    ceq = f["equity"].astype(float)
    out = ni / ceq.where(ceq > 0)          # equity <= 0 is a sign flip -> NaN
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    family="profitability",                # Phase C, 2026-10-01: Cat.Economic "profitability" (decision phase_c_family_partition)
    name="RoE",
    col="f_roe",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high RoE is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.netinc", "SF1.equity"),
    osap_acronym="RoE",
    source="Haugen and Baker 1996 (Journal of Financial Economics)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="netinc (ART TTM) / equity (ART); equity <= 0 -> NaN; equity includes preferred",
    field_mappings=(
        ("compustat.ni", "SF1.netinc (ART)",
         "TTM as of the latest filing, not fiscal year + 6-month lag; parent NI after NCI, before preferred dividends (this is ni, not ib)"),
        ("compustat.ceq", "SF1.equity (ART)",
         "includes preferred stock (OSAP ceq excludes it; ruling book_equity_preferred_terms); same filing as the numerator"),
        ("guard", "equity > 0", "equity <= 0 -> NaN (OSAP keeps sign-flipped negative-book and +/-inf zero-book rows); not in OSAP"),
        ("filter abs(prc)>5", "not reproduced", "harness universe is price >= $1"),
    ),
)
