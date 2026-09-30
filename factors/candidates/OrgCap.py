"""
OrgCap — organizational capital: a depreciating (15% a year) stock of past
SG&A-plus-R&D spending, scaled by assets and standardised within the firm's
Fama-French 17 industry. Firms that have accumulated more knowledge and
brand capital per dollar of assets than their industry peers may earn more.

OSAP: OrgCap, Eisfeldt and Papanikolaou 2013, Journal of Finance (Table 4A.1).
Predicted sign: + (SignalDoc Sign = +1: a HIGH industry-standardised value is the
long side; ascending=True).
Spec: osap_source/cache/b4e911e6/OrgCap/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Annual series, SF1 dimension ARY (fiscal-year level; a flow summed annually, so
  ART/ARQ would double-count or smear). Read on the MARKET scope
  (ctx.market_context(): every listed common stock that traded in the signal month)
  because OSAP winsorises and standardises across all of CRSP x Compustat.
    x_k   = SF1.sgna.fillna(0) + SF1.rnd.fillna(0)    (OSAP: xsga.fillna(0); Compustat
                                                       xsga includes R&D)
    chain = the firm's DECEMBER fiscal years (reportperiod month == 12), oldest first,
            known at the signal (datekey <= signal, restatement-safe), ending at the
            latest filed ARY row. The latest row must itself be a December year end.
    y     = 4 * x_0 at the first year, then y_k = 0.85 * y_{k-1} + x_k
            (closed form: y = sum_j 0.85^j x_{n-1-j}, with the oldest term x_0 given
            weight 4 * 0.85^(n-1)).
    STRICT gap rule (OSAP): if the December years are not consecutive anywhere in the
            chain (a missing fiscal year, a non-December year inside it, two rows in one
            calendar year), y is NaN for that firm from then on, i.e. at every later
            signal. There is no restart of the chain after a gap.
    raw   = y / SF1.assets (assets of the latest row, > 0 guarded); raw == 0 -> NaN.
    Winsorise raw at its 1st (np.percentile "lower") and 99th ("higher") percentile
            across the market cross-section of non-missing values (clip, as OSAP's
            winsor2), BEFORE the industry statistics.
    Industry: FF17 from current TICKERS.siccode through harness.industry.ff17; names
            with no FF17 or siccode == 9999 are dropped. Industry mean and standard
            deviation (ddof = 1, pandas) are taken over ALL remaining market names,
            financials included; z = (clipped raw - industry mean) / industry std
            (std must be > 0). THEN financials (SIC 6000-6999) and missing-SIC names
            are set NaN, as OSAP does. The standardisation is signal definition (it is
            part of the published variable), not the harness's sector ranking.
            Only universe IDs are returned for scoring.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with constant x gives a
  stock y = x / 0.15 (over a long chain), a continuous value. A firm with zero
  sgna + rnd in every year has raw == 0 and is set NaN (OSAP does the same).
  What share of the universe does nothing? Spec measured (23 December probe months,
  1998-12..2020-12) the modal share of the final industry z-score at 0.19%..0.65%
  (mean 0.36%); no mass point. Preflight is run by the coordinator.
  Tie handling: null (raw == 0 -> NaN, non-positive assets -> NaN, zero industry
  std -> NaN); no floored denominator; the harness average-ranks the rest.

DEVIATIONS FROM OSAP:
  - xsga: sgna + rnd. sgna is the as-reported SG&A line: EXCLUDES R&D (added back) and
    INCLUDES D&A where the filer reports it inside SG&A (Compustat xsga excludes D&A;
    ~36% of non-financial universe-proxy rows embed >= 90% of D&A per the field map).
    field_map status approx.
  - GNP deflator OMITTED. OSAP divides each monthly xsga by the GNP price deflator of
    that month. All December-year-end firms at one signal date share the same deflator
    path, so this is a common weighting of vintages, not a firm-specific term; it is not
    strictly rank-invariant. Spec measured the within-universe Spearman of the final
    industry-z between the nominal recursion and the deflated one at 0.9988..1.0000
    (mean 0.999) over 23 December probes. No macro table is held; no external constant
    is written into this file.
  - Truncated history. The snapshot's SF1 begins 1997Q4 (a few ARY rows reach back to
    FY1992), where OSAP's chain starts at each firm's first Compustat year (often the
    1950s-1980s). The initial term 4 * x_0 is therefore applied to the first December
    year SEEN, and carries 0.85^(n-1) of a mis-scaled initial stock. Spec measured the
    sensitivity (chain restarted 7 years before the end versus the full available chain):
    Spearman of the final industry z 0.994..1.000 (mean 0.997) over 23 probes, identical
    through 2002 where chains are <= 7 years. Median chain length of scored names: 1 at
    1998-12, 2 at 1999-12, 3 at 2000-12, 6 at 2003-12, 11 at 2008-12; 82% of scored names
    have <= 3 years at 1999-12. The early months (1999-2002) are essentially
    (SG&A + R&D) / assets over 1-4 years, a different signal in character from the
    published multi-decade stock.
  - History bound. The recursion reads up to 40 ARY rows per firm through ONE
    fundamentals_history call (ARY rows per ticker on this snapshot: maximum 34), so
    nothing is cut; the chain is the full available history. lookback_months = 480
    (40 fiscal years) states that reach; preflight will warn the read reaches before the
    panel start, which is the declared truncation, not a coverage defect.
  - Annual fold instead of OSAP's monthly rows. OSAP runs the recursion on monthly
    rows (a 12-row initialisation, then lag 12) for months the firm is in CRSP; here
    it is the equivalent once-a-year fold on fiscal years. Edge cases where OSAP's rows
    are cut by a CRSP-absent month are not reproduced.
  - Timing: OSAP enters a fiscal year at datadate + 6 months and holds 12 months. Here
    the latest ARY row known at the signal (datekey bound, no extra lag), held until the
    next is filed, at most max_fundamental_age_months (15); the signal is fresher by the
    3-4 months between year end and the filing.
  - Dec year end: reportperiod month == 12 (not calendardate, which is quarter-end
    normalised and would pass January year ends). Non-December year ends are NaN, as in
    OSAP.
  - Industry: current TICKERS.siccode stands in for CRSP sicCRSP (history not held), and
    it feeds the signal VALUE through the industry means (known_trap
    current_sic_signal_values; look-ahead through reclassification, declared).
  - Assets guard: raw = y / assets only where assets > 0 (OSAP nulls only at == 0); differs
    only for a negative-assets data error.
  - Universe of the statistics: the market scope is every listed common stock that
    traded in the signal month (OSAP: CRSP x Compustat with SignalMasterTable rows);
    no price, size or liquidity screen.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.industry import ff17

_DECAY = 0.85        # OSAP a = 0.85 (15% annual depreciation)
_INIT = 4.0          # OSAP init = 4 * first-year xsga
_N_ARY = 40          # ARY rows read per firm; the snapshot maximum is 34 (nothing cut)
_FIRST_FY = 1997     # declared first fiscal year of the recursion (SF1 starts FY1997)


def _orgcap_raw(mc):
    """y / assets per market ID: the OSAP recursion folded over consecutive
    December fiscal years, strict NaN after any gap. Indexed by ID."""
    h = mc.fundamentals_history(["sgna", "rnd", "assets"], _N_ARY, dimension="ARY")
    if h.empty:
        return pd.Series(dtype=float)
    h = h.sort_values(["ID", "reportperiod"], kind="mergesort")
    # fiscal year-end = reportperiod - 7 days, so 52/53-week December filers whose year
    # ends Jan 1-3 count as December (as Compustat dates them) and Nov-30 filers ending
    # Dec 1-3 do not (alpha_review batch17 major 1)
    fy = h["reportperiod"] - pd.Timedelta(days=7)
    h = h.assign(fy_month=fy.dt.month, fy_year=fy.dt.year)

    # the current record (latest ARY row known) must be a December year end
    latest = h[h["q_back"] == 0].set_index("ID")
    dec_ids = latest.index[latest["fy_month"] == 12]

    # December years from the declared first fiscal year (FY1997) only: stray earlier rows
    # would read as a gap at the snapshot start (major 2); one row per fiscal year (minor 3)
    d = h[(h["fy_month"] == 12) & (h["fy_year"] >= _FIRST_FY) & h["ID"].isin(dec_ids)].copy()
    sort_cols = ["ID", "fy_year"] + (["datekey"] if "datekey" in d.columns else [])
    d = d.sort_values(sort_cols, kind="mergesort").drop_duplicates(["ID", "fy_year"], keep="last")
    d["year"] = d["fy_year"]
    d["dy"] = d.groupby("ID")["year"].diff()
    d["bad"] = d["dy"].notna() & (d["dy"] != 1)          # not consecutive December years
    gap = d.groupby("ID")["bad"].any()

    d["j"] = d.groupby("ID").cumcount(ascending=False)    # 0 = latest year
    d["first"] = d.groupby("ID").cumcount() == 0           # oldest year in the chain
    x = d["sgna"].astype(float).fillna(0.0) + d["rnd"].astype(float).fillna(0.0)
    w = _DECAY ** d["j"].to_numpy(dtype=float) * np.where(d["first"].to_numpy(), _INIT, 1.0)
    y = pd.Series(w * x.to_numpy(), index=d["ID"].to_numpy()).groupby(level=0).sum()
    y = y.where(~gap.reindex(y.index).fillna(True).astype(bool))

    at = latest["assets"].astype(float).reindex(y.index)
    raw = y / at.where(at > 0)
    return raw.where(raw != 0).replace([np.inf, -np.inf], np.nan)


def _compute(ctx):
    mc = ctx.market_context()
    raw = _orgcap_raw(mc)
    if raw.empty:
        return pd.Series(np.nan, index=ctx.ids)

    # winsorise 1/99 across the market cross-section (clip), before industry stats
    v = raw.dropna()
    if len(v) > 1:
        lo = np.percentile(v.to_numpy(), 1, method="lower")
        hi = np.percentile(v.to_numpy(), 99, method="higher")
        raw = raw.clip(lower=lo, upper=hi)

    # FF17 industry on current siccode (declared); stats over all classified names
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"], scope="market")["siccode"],
                        errors="coerce").reindex(raw.index)
    ind = ff17(sic.reset_index(drop=True)).set_axis(raw.index)
    ok = ind.notna() & sic.notna() & (sic != 9999) & raw.notna()
    g = raw[ok].groupby(ind[ok])
    mean = g.transform("mean")
    std = g.transform("std").where(lambda s: s > 0)     # needs >= 2 members and spread
    z = (raw[ok] - mean) / std

    # financials (SIC 6000-6999) are dropped AFTER the statistics, as OSAP does
    fin = (sic[ok] >= 6000) & (sic[ok] < 7000)
    z = z.where(~fin).replace([np.inf, -np.inf], np.nan)

    out = z.reindex(ctx.ids.astype(str))
    out.index = ctx.ids
    return out


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="OrgCap",
    col="f_orgcap",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH industry-standardised organizational capital is the long side
    weight=1.0,
    inputs=("SF1.sgna", "SF1.rnd", "SF1.assets", "TICKERS.siccode"),
    osap_acronym="OrgCap",
    source="Eisfeldt and Papanikolaou 2013 (Journal of Finance)",
    lookback_months=480,            # recursion reads up to 40 ARY fiscal years (snapshot max 34); reaches before the panel start by design
    dimension="ARY",
    notes="0.85-decay stock of 4*first + (sgna+rnd) over consecutive December ARY years (strict NaN after a gap), / assets, clip 1/99 on market, FF17 z-score on current siccode, financials NaN; deflator omitted",
    field_mappings=(
        ("compustat.xsga", "SF1.sgna + SF1.rnd (ARY), each .fillna(0)",
         "approx: sgna excludes R&D (added back) and includes D&A for some filers; OSAP's own xsga.fillna(0) kept; sgna == 0 (vendor zero-fill) is a zero as in OSAP"),
        ("compustat.at", "SF1.assets (ARY, latest December year)", "assets > 0 guarded (OSAP nulls at == 0 only)"),
        ("compustat.datadate", "SF1.reportperiod month == 12",
         "not calendardate (quarter-end normalised); the latest ARY row must be a December year end and the chain consecutive December years"),
        ("gnpdefl", "omitted",
         "no macro table held; common to all December-FYE firms at a date; spec Spearman vs deflated recursion 0.999 mean (0.9988..1.0000)"),
        ("crsp.sicCRSP / compustat.sic", "TICKERS.siccode (CURRENT, market scope)",
         "approx: current classification feeds the signal value via FF17 mean/std (known_trap current_sic_signal_values)"),
        ("recursion init", "4 * first December ARY year seen",
         "snapshot starts FY1997 (a few rows FY1992+), OSAP starts at the firm's first Compustat year; early months are short-chain SG&A+R&D / assets; spec init sensitivity Spearman 0.994..1.000 (mean 0.997)"),
        ("gap rule", "strict NaN after any non-consecutive December year",
         "OSAP fill_date_gaps then NaN propagation; no restart variant"),
        ("winsorise + FF17 z", "in-factor, market scope",
         "np.percentile lower 1 / higher 99 clip over all non-null market names, then (x - mean_FF17)/std_FF17 over all classified names incl. financials, then financials NaN"),
    ),
)
