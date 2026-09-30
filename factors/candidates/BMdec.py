"""
BMdec — book equity over the prior December's market equity, held June to May
(the Fama-French 1992 timing); a high book-to-market firm is priced cheaply
against its accounting equity.

OSAP: BMdec, Fama and French 1992, Journal of Finance (Table 3, Ln(BE/ME)).
Predicted sign: + (high BMdec earns higher returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/BMdec/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  BE     = fiscal-year Y-1 book equity, paired with the December Y-1 ME (the
           project's BMdec convention, harness/data_layer.py FF3 block): SF1
           dimension ARY (annual, as reported), the fiscal year whose
           reportperiod falls in calendar year Y-1, where Y-1 is the year of the
           December whose ME is used (Jun..Dec signals: signal year - 1; Jan..May
           signals: signal year - 2); the latest such filing with
           datekey <= signal date (point-in-time, via ctx.fundamentals_history).
           SE = SF1.equity, or SF1.assets - SF1.liabilities where equity is null;
           BE = SE + SF1.taxliabilities.fillna(0); preferred = 0.
           Names whose filing is not reported in USD (fxusd != 1) are set
           missing. SF1 has equityusd but the other inputs are paired in one
           currency with the USD market cap; the gate is kept for consistency
           (<=0.06% of members).
  ME_Dec = DAILY.marketcap (millions USD, scaled to raw USD by config
           universe.daily_marketcap_scale via ctx.cfg) at the December
           business month-end that OSAP's June-May rule selects, read through
           ctx.at_month_end: with m the calendar month of the signal date,
           months_back = m for m in Jun..Dec (Jun 6, Dec 12: the December of
           the prior year) and m + 12 for m in Jan..May (Jan 13, May 17: the
           December of the year before that). Net: June Y through May Y+1 uses the
           December Y-1 market cap, held fixed. Numerator (BE) and denominator (ME)
           are both fixed June Y..May Y+1 and both refer to Dec Y-1 / FY Y-1; BMdec
           changes only at each June re-pairing (and when a late filer's FY Y-1
           10-K arrives inside the window).
  BMdec  = BE / ME_Dec. Raw ratio, no log: ln is monotone, so ranks, deciles
           and rank-IC match the paper's ln(BE/ME).
  Denominator guarded `> 0` (zero or missing December cap -> NaN).

NEGATIVE BOOK EQUITY: kept, following OSAP (BMdec.py applies no positivity
  filter; a negative BE/ME is a real, lowest-value observation and lands in D1
  under ascending=True). The composite's Value leg drops equity <= 0; BMdec
  does not. The guard `> 0` sits on the DENOMINATOR (market cap), where a
  negative value would be a sign flip; a negative numerator is a legitimate
  ratio, not an error. Exact zero equity is 0.01% of non-null (data errors)
  and stays as a value of 0.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Within June..May both BE and
  ME_Dec are frozen, so BMdec is piecewise-constant in time, but it is a
  continuous ratio ACROSS firms: there is no shared default value and no
  zero-fill that creates one (taxliabilities.fillna(0) only fills the 0.03%
  null rows and is added to a non-zero equity).
  What share of the universe does nothing? ~0% at any single value; the only
  discrete value is equity + taxliabilities == 0 (~0.01%).
  Tie handling: null (ME_Dec <= 0 or missing, fxusd != 1, no equity and no
  assets/liabilities become NaN and blend_ranks renormalises). Ties otherwise
  negligible.

DEVIATIONS FROM OSAP:
  - pstk/pstkrv/pstkl: Sharadar has no preferred-stock field. OSAP's
    BE = SE + txditc - PS; preferred is NOT removed here, so BE is too high by
    the preferred carrying value for preferred issuers (logged ruling
    book_equity_preferred_terms: the term only adjusts book equity -> approx).
    OSAP's BE (hence BMdec) is missing when all three preferred items are
    missing; that conditioning is not reproducible, so coverage is broader.
  - seq/ceq: SF1.equity is parent equity including preferred; the
    `ceq + pstk` branch is dead code under the same column.
  - txditc: SF1.taxliabilities, a generic tax-liability line (34-45% exact
    zero in the universe), filled with 0 as OSAP fills txditc; not deferred
    taxes and investment tax credit.
  - Numerator timing: SF1 ARY fiscal-year Y-1 value, known by its filing date
    (datekey <= signal date), instead of OSAP's annual Compustat value made
    available 6 months after fiscal year-end. The 6-month lag is not reproduced;
    a 10-K filed after June (late filer) enters that month only once filed, and
    the name is NaN until then. ARY carries the as-reported annual figure with
    SF1's own freshness cap (max_fundamental_age_months = 15) on the latest filing.
  - ME: DAILY.marketcap is company-level (all classes) at the primary ticker,
    against OSAP's per-permno |prc| * shrout; few-percent level difference on
    a small share of multi-class names. The December row must fall within 7
    calendar days before the December business month-end.
  - Data start: DAILY begins 1998-12-01, so there is no December 1997 market
    cap and Jan-May 1999 signals are NaN (5 of 276 decision months); the
    signal is fully formed from June 1999.
  - currency: non-USD reporters (<=0.06% of universe members) nulled via
    fxusd == 1 rather than converted (equityusd exists; kept null for consistency).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _dec_lag(month):
    """Months back from the signal month-end to the December whose market cap
    OSAP's June-May rule uses: Jun..Dec -> m, Jan..May -> m + 12."""
    return int(month) if month >= 6 else int(month) + 12


def _compute(ctx):
    k = _dec_lag(ctx.signal_asof.month)
    # calendar year of the December whose ME is used = the fiscal year Y-1 to read
    dec_year = ctx.signal_asof.year - (1 if ctx.signal_asof.month >= 6 else 2)

    h = ctx.fundamentals_history(["equity", "assets", "liabilities", "taxliabilities", "fxusd"],
                                 n_periods=4, dimension="ARY")
    h = h[pd.DatetimeIndex(h["reportperiod"]).year == dec_year]
    h = (h.sort_values(["ID", "reportperiod", "datekey"], kind="mergesort")
          .drop_duplicates("ID", keep="last").set_index("ID"))
    f = h.reindex(ctx.ids)
    equity = f["equity"].astype(float)
    fallback = f["assets"].astype(float) - f["liabilities"].astype(float)
    se = equity.fillna(fallback)
    be = se + f["taxliabilities"].astype(float).fillna(0.0)
    be = be.where(f["fxusd"].astype(float) == 1.0)

    scale = float(ctx.cfg["universe"].get("daily_marketcap_scale", 1))
    me = ctx.at_month_end("DAILY", ["marketcap"], k)["marketcap"].astype(float) * scale
    me = me.reindex(be.index)

    return be / me.where(me > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BMdec",
    col="f_bmdec",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high BMdec predicts high returns
    weight=1.0,
    dimension="ARY",                # fiscal-year book equity paired with the December ME (passed explicitly in _compute)
    inputs=("SF1.equity", "SF1.assets", "SF1.liabilities", "SF1.taxliabilities",
            "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="BMdec",
    source="Fama and French 1992 (Journal of Finance)",
    lookback_months=28,             # May signal reads FY Y-1 ending as early as Jan Y-1 (28m); the December ME is 13-17m
    notes="ARY FY(Y-1) (equity + taxliabilities) / December(Y-1) DAILY.marketcap, June-May; negative BE kept; preferred not removed",
    field_mappings=(
        ("compustat.seq", "SF1.equity (ARY, FY with reportperiod in calendar Y-1, datekey <= signal)",
         "parent equity including preferred; filing-date availability vs OSAP annual + 6-month lag; fallback assets - liabilities when null; fxusd != 1 -> NaN"),
        ("compustat.ceq", "SF1.equity", "same column as seq; the `ceq + pstk` branch is dead code"),
        ("compustat.txditc", "SF1.taxliabilities.fillna(0)",
         "generic tax-liability line, not deferred taxes + ITC; 34-45% exact zero in universe; zero-filled as OSAP fills txditc"),
        ("compustat.pstk/pstkrv/pstkl", "omitted",
         "no SF1 field; preferred not removed from BE (ruling book_equity_preferred_terms); OSAP's missing-preferred conditioning not reproduced"),
        ("crsp.me (December)", "DAILY.marketcap x cfg daily_marketcap_scale via ctx.at_month_end(k)",
         "company-level cap at the December business month-end (k = m for Jun..Dec, m+12 for Jan..May); no Dec-1997 row, so Jan-May 1999 NaN"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (equityusd exists; kept for consistency); <=0.06% of universe names"),
    ),
)
