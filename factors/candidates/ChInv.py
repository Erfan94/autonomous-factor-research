"""
ChInv — 12-month change in inventory scaled by average total assets (Thomas
and Zhang 2002, Delta Invent); firms that build inventory are predicted to
earn LOWER returns, so the long leg is LOW (or negative) inventory change.

OSAP: ChInv, Thomas and Zhang 2002, Review of Accounting Studies.
Predicted sign: - (SignalDoc Sign = -1: high value, low return).
Spec: osap_source/cache/b4e911e6/ChInv/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["inventory", "assets"])   (ART default; latest
      filing known at the signal and the same fiscal period one year
      earlier, aligned by reportperiod within 45 days)
  inv, inv_lag = inventory and year-ago inventory; a NULL inventory is
      treated as 0 ONLY where that period's filing exists (reportperiod /
      reportperiod_lag present), matching OSAP's zero-fill of invt. The NaN
      that fundamentals_yoy returns for a missing year-ago period is never
      filled.
  ChInv = (inv - inv_lag) / ((assets + assets_lag) / 2)
  Guards: average assets <= 0 or null (either assets null) -> NaN; missing
  year-ago period -> NaN; non-finite -> NaN.
  Inventory and assets are balance-sheet LEVELS (ART equals ARQ on the same
  reportperiod): no flow, no TTM smear, no dimension override, and both are
  in the filer's reporting currency so the ratio needs no fxusd gate.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (inventory
  unchanged year on year). These are overwhelmingly firms with no inventory
  at all (inventory 0 or null in both periods: services, software, banks,
  REITs), for which the signal is undefined, not zero.
  What share of the universe does nothing? Measured by the field-checker on
  the harness universe: inventory 0 or null in BOTH periods is 34-43% of
  computable names (34.7% / 34.1% / 42.5% at 1999-12 / 2008-12 / 2020-12).
  A genuine exactly-zero change on NONZERO inventory is at most one name per
  month. Residual modal share after the rule below: 0.1%.
  Tie handling: null (restrict the sample). ChInv is set to NaN wherever
  inventory is 0 or null in BOTH periods; blend_ranks renormalises. It is
  kept wherever inventory is nonzero in at least one period (including zero in
  one period and nonzero in the other). A null inventory on an existing filing
  is zero-filled first (as OSAP zero-fills invt), and only then is the both-zero
  case set to NaN, so null-against-null and null-against-0 are removed while
  null-against-positive is kept as a change from/to 0. Coordinator decision:
  the signal is conceptually undefined for a firm with no inventory, so the
  tied block is removed rather than ranked as a flat middle.
  No noise or secondary key is used to break ties.
  Measured spurious-tail share (scored names whose inventory is null at exactly
  one of the two dates and > 0 at the other, so the zero-fill yields a +/-
  inventory/avg-assets that is an artefact of a vendor null): 0.00% / 0.00% /
  0.00% of scored names at signals 1999-12 / 2008-12 / 2020-12 (0 of 1488 /
  1162 / 1124). Sharadar stores 0, not null, for an absent inventory item (at
  most one null per date on the harness universe), so the OSAP zero-fill is
  effectively inert here.

DEVIATIONS FROM OSAP:
  - OSAP keeps the inventory-free firms at ChInv = 0; here they are NaN (the
    tie rule above). This changes the population relative to OSAP.
  - timing: latest ART filing (0-3 months old, at most
    max_fundamental_age_months = 15) against the same fiscal period one year
    earlier (rolling four-quarter change, refreshed quarterly), not OSAP's
    fiscal-year values with datadate + 6 months held 12 months. The 6-month
    lag is not reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not OSAP's shift(12)
    monthly rows, which misalign after a skipped fiscal year; a stale filing
    yields NaN rather than a false exact-zero change.
  - upstream Compustat row filter (non-null at, prcc_c, ni) not reproduced:
    a difference in sample, not in value; null assets -> NaN.
  - early window: SF1 calendardate starts 1997Q4, so the first 1999 signal
    months can lack a year-ago period (NaN, not back-filled).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["inventory", "assets"])
    have_now = y["reportperiod"].notna()
    have_ago = y["reportperiod_lag"].notna()

    inv = y["inventory"].astype(float)
    inv_lag = y["inventory_lag"].astype(float)
    # OSAP zero-fills invt: null -> 0, but only where the filing exists.
    inv = inv.where(~(have_now & inv.isna()), 0.0)
    inv_lag = inv_lag.where(~(have_ago & inv_lag.isna()), 0.0)

    avg_assets = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    chg = (inv - inv_lag) / avg_assets.where(avg_assets > 0)

    # Tie rule: inventory 0 in BOTH periods -> signal undefined (no inventory).
    both_zero = (inv == 0) & (inv_lag == 0)
    out = chg.where(have_now & have_ago & ~both_zero)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChInv",
    col="f_chinv",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW inventory growth is attractive
    weight=1.0,
    inputs=("SF1.inventory", "SF1.assets"),
    osap_acronym="ChInv",
    source="Thomas and Zhang 2002 (Review of Accounting Studies)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="(inventory - year-ago inventory) / average assets; NaN where inventory is 0/null in both periods; sign -1",
    field_mappings=(
        ("compustat.invt", "SF1.inventory (ART)",
         "null -> 0 only where the period's filing exists (OSAP zero-fill); both-periods 0 -> NaN (deviation: OSAP keeps them at 0)"),
        ("compustat.at", "SF1.assets (ART)",
         "average of latest and year-ago assets, guard > 0; null -> NaN (OSAP drops null at)"),
        ("invt/at shift(12)", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance), not 12 monthly rows; missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
