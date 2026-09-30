"""
InvGrowth - year-over-year growth of inventory (deflated), among non-utility,
non-financial firms; high inventory growth = overinvestment / slowing demand.

OSAP: InvGrowth, Belo and Lin 2012 (Review of Financial Studies, Table 2A EW;
SignalDoc Acronym2 InvenGr). Predicted sign: - (SignalDoc Sign = -1: LONG low
growth, so ascending=False).
Spec: osap_source/cache/b4e911e6/InvGrowth/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["inventory", "assets", "ppnenet"], years=1)
  the latest ART filing known at the signal and the filing for the same fiscal
  period one year earlier, aligned by reportperiod (45-day tolerance):
    InvGrowth = inventory / inventory_lag - 1, inventory_lag > 0 required.
  inventory is a balance-sheet LEVEL (ART equals ARQ on the same reportperiod),
  so there is no four-quarter smear and no dimension override (ART default).

SAMPLE SCREENS INSIDE THE SIGNAL (OSAP's own, NaN output, not a universe change):
  - SIC: drop where the first digit of the SIC code is 4 (transport / utilities)
    or 6 (financials), read from TICKERS.siccode via ctx.ticker_meta. A null SIC
    is KEPT, as in OSAP (the string "nan" does not start with 4 or 6). That SIC is
    TODAY's vendor classification, not the code in force in the month scored: a
    declared look-ahead (field_map ruling current_sic_signal_values; 12-14% of
    names reclassified since 1998).
  - assets > 0 (current filing).
  - ppnenet > 0 or missing. Sharadar fills 0 for "not reported", so a value of 0
    cannot be told from a missing one; it is treated as missing and KEPT (OSAP
    keeps NaN ppent and does not zero-fill it). Only negative ppnenet is dropped.
    Effect: ~0.4% of names with positive lagged inventory.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (inventory equal to
  the year-ago filing to the dollar), but that needs a tie to the dollar: 0.00-0.39%
  of scored names (mean 0.10%) per the spec measurement. The real mass point is
  ZERO INVENTORY. 46% of ART rows are exactly 0 (vendor zero-fill = OSAP's own
  zero-fill of invt); both zero -> 0/0, NaN in OSAP and NaN here (30-43% of the
  universe goes unscored; this is OSAP's rule, not a deviation). Inventory going
  from positive to 0 gives exactly -1.0, a second mass point at the bottom: mean
  0.71% of scored names, max 2.15% (1999-2000), far below the 10% preflight limit.
  Tie handling: REMOVE where both periods are zero (the lag > 0 guard); the -1.0
  block is kept as OSAP's own value (a real liquidation of inventory, not a vendor
  default) and the harness averages its ranks; ascending=False puts it in the long
  leg. A lagged inventory of 0 with positive current inventory (OSAP's pandas output
  is inf, kept by its dropna; ~0.69% of the universe) -> NaN.
  Expected scored coverage 44-57% of the universe from 1999-03; the first three
  signal months (1998-12..1999-02) are thinner (28-34%) because the year-ago ART
  filing is sparse at the snapshot start.

DEVIATIONS FROM OSAP:
  - GNP deflator omitted. invt/defl_t / (invt_{t-12}/defl_{t-12}) - 1 equals
    (invt_t/invt_{t-12}) * (defl_{t-12}/defl_t) - 1, where both deflator values are
    month-constants shared by every firm: the score is a positive affine map of the
    nominal ratio within a month, so sector-relative ranks, IC and deciles are
    identical. Exact for the harness; FRED GNPCTPI is not in the snapshot.
  - SIC is the current classification (look-ahead, above).
  - ppnenet == 0 treated as missing and kept (above).
  - lagged inventory == 0 with positive current inventory -> NaN (OSAP: inf).
  - a null current or year-ago inventory is left NaN (OSAP zero-fills invt, but the
    0.04% Sharadar nulls are missing filings, not reported zeros; vendor 0 is
    already the zero-fill).
  - Timing: OSAP reads fiscal-year invt available at datadate + 6 months, held 12
    months (signal 6-17 months stale, changes once a year). Here the latest ART
    filing (quarterly refresh, four updates a year) against the filing whose
    reportperiod is one year earlier; OSAP's 6-month annual lag is not reproduced.
  - OSAP's calendar-12-month row merge (NaN across a fiscal-year change or gap) is
    replaced by the reportperiod-aligned year-ago filing.
  - OSAP's shrcd / price / NYSE-breakpoint filters and EW decile portfolios are the
    harness's, not reproduced.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["inventory", "assets", "ppnenet"], years=1)

    inv = y["inventory"].astype(float)
    inv_lag = y["inventory_lag"].astype(float)
    # lagged inventory must be positive: 0 gives inf (OSAP) or 0/0; null stays NaN.
    score = (inv / inv_lag.where(inv_lag > 0)) - 1.0

    # OSAP sample screens (NaN, not a universe change).
    assets = y["assets"].astype(float)
    ppe = y["ppnenet"].astype(float)
    ok = (assets > 0) & (ppe.isna() | (ppe >= 0))   # 0 kept: vendor 0 = "not reported"

    # SIC first digit 4 or 6 dropped; null SIC kept (OSAP: "nan" does not start with 4/6).
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")
    sic = sic.reindex(score.index)
    first = sic.dropna().astype(np.int64).astype(str).str[0]
    drop_sic = pd.Series(False, index=score.index)
    drop_sic.loc[first.index] = first.isin(["4", "6"])

    return score.where(ok & ~drop_sic).replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="InvGrowth",
    col="f_invgrowth",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW inventory growth is attractive
    weight=1.0,
    inputs=("SF1.inventory", "SF1.assets", "SF1.ppnenet", "TICKERS.siccode"),
    osap_acronym="InvGrowth",
    source="Belo and Lin 2012 (Review of Financial Studies)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m filing lag
    # No history_months: no SEP price window is read. No dimension override: inventory is a level.
    notes=("inventory / year-ago inventory - 1 (ART, reportperiod-aligned); lag > 0; SIC 4xxx/6xxx "
           "(current) dropped, null SIC kept; assets > 0; ppnenet >= 0 or null; GNP deflator omitted "
           "(rank-invariant); sign -1"),
    field_mappings=(
        ("compustat.invt, invt_lag12", "SF1.inventory (ART) via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tol), not shift(12); lag == 0 -> NaN (OSAP inf / 0/0); null stays NaN"),
        ("gnpdefl (FRED GNPCTPI)", "omitted",
         "month-constant across firms: positive affine map of the nominal ratio, ranks/IC/deciles identical"),
        ("sic (first digit 4 or 6 dropped)", "TICKERS.siccode (current)",
         "CURRENT classification (look-ahead, current_sic_signal_values ruling); null kept as in OSAP"),
        ("at > 0", "SF1.assets (ART)", "latest filing level"),
        ("ppent > 0 or NaN", "SF1.ppnenet (ART)", "0 = vendor 'not reported', treated as missing and kept; negative dropped"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "quarterly refresh vs annual; OSAP's 6-month lag not reproduced"),
    ),
)
