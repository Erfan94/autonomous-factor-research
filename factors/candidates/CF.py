"""
CF — cash flow to market: (income before extraordinary items + depreciation and
amortisation) / market equity. A firm whose cash earnings are large against its
price is cheap.

OSAP: CF, Lakonishok, Shleifer and Vishny 1994, Journal of Finance (Table 6
panel 1). Predicted sign: + (SignalDoc Sign = +1, high CF earns high returns;
long D10, short D1; ascending=True).
Spec: osap_source/cache/b4e911e6/CF/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Latest known ART filing (trailing-four-quarter flows, same row for all terms):
    ib  = SF1.netinc + SF1.netincdis
    dp  = SF1.depamor, null read as 0 only when the same row's revenue and
          netinc are present (see NULL HANDLING)
    CF  = (ib + dp) / ctx.universe["mkt_cap_usd"]   (cap > 0 guard)
  Names whose filing is in a non-USD reporting currency (fxusd != 1) are set
  missing: the numerator is reporting currency, the denominator USD.

  ib, the sign of netincdis: netincdis carries the OPPOSITE sign to the income
  it describes (the vendor reports the discontinued-operations line as an
  adjustment to get back to continuing income). Checked on real ARY filings in
  this snapshot: PFE 2013 netinc 22,003 / netincdis -10,662 (Zoetis exchange
  gain; continuing ops 11,341); JNJ 2023 35,153 / -21,827 (Kenvue exchange gain;
  continuing 13,326); AGN 2016 14,973 / -15,914 (generics-divestiture gain);
  MRK 2021 13,049 / -704 (spin income; continuing 12,345); GE 2019 -4,979 /
  +5,335 (discontinued LOSS; continuing +356); GE 2018 -22,355 / +1,726
  (continuing -20,629). So continuing-operations income = netinc + netincdis,
  which is Compustat ib's concept (before extraordinary items and
  discontinued operations, before preferred dividends; netinc is before
  prefdivis, unlike netinccmn). netincdis is non-null on 100% of ART rows with
  netinc present (88.3% exact zero), so no fill is needed; a null stays NaN.

NULL HANDLING:
  - ib: netinc null -> NaN (OSAP does not zero-fill ib). Negative CF is kept
    (OSAP does not trim it; winsorisation belongs to the harness).
  - dp: OSAP zero-fills dp. A null ART depamor is read as zero ONLY when the
    SAME filing row carries the other trailing-four-quarter flows (revenue and
    netinc non-null), i.e. the filer reported a full TTM but no D&A add-back.
    Where those flows are also missing, the row is the early-1998 TTM gap (ART
    needs four quarters of history, SF1 starts 1998) and the score stays NaN
    rather than becoming a spuriously ib-only value.
  - dimension: ART default. Universe coverage of the ART numerator is 57-59% at
    1998-12..1999-02 and ~92% from 1999-03, above the 40% bar, so no ARY
    fallback.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? (ib + dp) / market cap: a firm
  with no new filing keeps ib + dp fixed while market cap moves every month, so
  CF moves continuously; there is no default value. Mass at exactly zero needs
  ib + dp == 0; netinc exact zero is ~0.01% and a zero-filled dp gives CF =
  ib / mve, not zero.
  What share of the universe does nothing? ~0% at any single value (modal-value
  share measured by the field-checker ~0.09%); preflight measures it.
  Tie handling: null (mkt cap <= 0, fxusd != 1 become NaN, blend_ranks
  renormalises). Residual ties are averaged by the harness.

DEVIATIONS FROM OSAP:
  - ib -> netinc + netincdis: TTM continuing-operations income before
    preferred dividends, after non-controlling interest (SF1 netinc is the
    parent share; Compustat ib is before the NCI deduction on some filers, a
    small residual). netinccmn was not used: it is after preferred dividends and
    includes discontinued operations (Compustat ibcom).
  - Timing: the numerator is a TTM sum to the latest filed quarter (0-3 months
    old, capped at 15) against OSAP's fiscal-year figure available 6 months
    after year-end and held 12 (6-17 months old). The 6-month lag is not
    reproduced.
  - dp -> depamor: the cash-flow add-back, which can include lease ROU
    amortisation from 2019 (ASC 842), not the income-statement line.
  - mve_permco -> DAILY.marketcap at the primary ticker's price, all-class
    shares (few-% level error on <=2% of names).
  - SignalDoc portfolio filter exchcd in (1,2) (NYSE and AMEX only, NASDAQ
    excluded) is a universe filter and is NOT reproduced; the harness universe
    includes NASDAQ names.
  - fxusd != 1 names nulled rather than converted (<=0.06% of universe members).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["netinc", "netincdis", "depamor", "revenue", "fxusd"])
    ni = f["netinc"].astype(float)
    # netincdis carries the opposite sign to discontinued-ops income:
    # continuing income = netinc + netincdis (checked on real filings, see docstring)
    ib = ni + f["netincdis"].astype(float)

    # dp zero-fill (OSAP): only where the same TTM row carries the other flows
    dp = f["depamor"].astype(float)
    flows_present = f["revenue"].notna() & ni.notna()
    dp = dp.where(dp.notna() | ~flows_present, 0.0)

    cf = (ib + dp).where(f["fxusd"].astype(float) == 1.0)
    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(cf.index)
    return cf / mcap.where(mcap > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CF",
    col="f_cf",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high CF predicts high returns
    weight=1.0,
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.depamor", "SF1.revenue", "SF1.fxusd",
            "DAILY.marketcap"),
    osap_acronym="CF",
    source="Lakonishok, Shleifer and Vishny 1994 (Journal of Finance)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="(netinc + netincdis + depamor) / market cap; ART TTM flows; dp zero-filled only on full-TTM rows; fxusd==1",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ART)",
         "netincdis sign is inverted vs the income it describes (PFE 2013, JNJ 2023, AGN 2016, MRK 2021, GE 2018/2019), so netinc + netincdis = continuing income before preferred dividends; netinccmn (= ibcom, after prefdivis, incl. discontinued ops) not used; after NCI; TTM to latest quarter vs OSAP fiscal year"),
        ("compustat.dp", "SF1.depamor (ART)",
         "TTM cash-flow add-back (incl. ROU amortisation from 2019); null read as 0 only when revenue and netinc of the same row are present, else NaN (early-1998 TTM gap)"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names; cap <= 0 -> NaN"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (reporting-currency numerator over USD cap); <=0.06% of universe names"),
        ("signaldoc.filter", "none", "exchcd in (1,2) is a universe filter, not reproduced; NASDAQ names included"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
