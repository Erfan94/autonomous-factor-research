"""
AM — total assets relative to market value of equity (Fama-French A/ME); a
high-assets-per-dollar-of-equity firm is priced cheaply against its asset base.

OSAP: AM, Fama and French 1992, Journal of Finance (Table 3, Ln(A/ME)).
Predicted sign: + (high AM earns higher returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/AM/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  AM = SF1.assets (ART, latest filing known at the signal date)
       / ctx.universe["mkt_cap_usd"] (DAILY.marketcap at the signal month-end,
       scaled to raw USD by the harness).
  Raw ratio, no log: ln is monotone, so ranks, deciles and rank-IC match the
  paper's ln(A/ME). Denominator guarded `> 0`; assets <= 0 is treated as
  missing (OSAP would emit 0 or a negative ratio). Names whose latest SF1
  filing is in a non-USD reporting currency (fxusd != 1) are set missing,
  because `assets` has no *usd variant and would mix currencies.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing
  keeps `assets` fixed but its market cap moves with price every month, so AM
  changes continuously; there is no default value and no zero-fill.
  What share of the universe does nothing? ~0% at any single value; the only
  discrete value is assets == 0 (~0.01% of non-null, data errors), nulled.
  Tie handling: null (assets <= 0, mkt cap <= 0, fxusd != 1 become NaN and
  blend_ranks renormalises). Ties otherwise negligible (continuous ratio).

DEVIATIONS FROM OSAP:
  - at: SF1 assets via ART at the latest filing with datekey <= signal date
    (10-K or 10-Q, balance-sheet level, usually 0-3 months old, at most
    max_fundamental_age_months = 15). OSAP uses the annual
    Compustat `at` made available 6 months after fiscal year-end and held 12
    months (6-17 months old). The 6-month lag is not reproduced.
  - mve_permco: DAILY.marketcap on the primary-class ticker (company-level,
    all-class shares x primary price) instead of CRSP shrout x |prc| summed over
    listed permnos of a permco; a few-percent level difference on <=2% of names.
  - currency: non-USD reporters (<=0.06% of universe members) nulled via
    fxusd == 1 rather than converted.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["assets", "fxusd"])
    assets = f["assets"].astype(float)
    assets = assets.where(assets > 0)
    assets = assets.where(f["fxusd"].astype(float) == 1.0)
    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(assets.index)
    return assets / mcap.where(mcap > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="AM",
    col="f_am",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high AM predicts high returns
    weight=1.0,
    inputs=("SF1.assets", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="AM",
    source="Fama and French 1992 (Journal of Finance)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="assets / market cap; ART latest filing over month-end DAILY.marketcap; non-USD reporters nulled",
    field_mappings=(
        ("compustat.at", "SF1.assets (ART)",
         "latest filing (usually 0-3 months old, capped at 15) vs OSAP annual + 6-month lag (6-17 months old); assets <= 0 -> NaN; fxusd != 1 -> NaN"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (assets has no *usd variant); <=0.06% of universe names"),
    ),
)
