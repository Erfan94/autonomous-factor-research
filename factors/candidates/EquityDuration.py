"""
EquityDuration — equity duration from a 10-year ROE / growth cash-flow projection:
the value-weighted average time to the projected equity cash distributions, scaled
by the market value of equity. Long-duration (growth-priced) equity is predicted to
earn LOWER returns, so the long leg is LOW EquityDuration.

OSAP: EquityDuration, Dechow, Sloan and Soliman 2004, Review of Accounting Studies
(Table 6A HDMLD). Predicted sign: - (SignalDoc Sign = -1: high value, low return).
Spec: osap_source/cache/b4e911e6/EquityDuration/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Inputs, all from ctx.fundamentals_yoy at the project-default ART dimension (latest
  filing known at the signal and the filing for the same fiscal period one year
  earlier, aligned by reportperiod, never by an as-of date):
    ib      = SF1.netinc + SF1.netincdis (TTM, latest filing). netincdis carries the
              OPPOSITE sign to the discontinued-operations income it describes (known
              trap sf1_netincdis_sign_inverted), so the sum is PLUS. netinccmn is not
              used (it is ibcom, after preferred dividends).
    ceq     = SF1.equity (latest), ceq_lag = SF1.equity of the filing four quarters
              earlier.
    sale    = SF1.revenue (TTM, latest), sale_lag = the TTM one year earlier.
    ME      = SEP.close x SF1.sharesbas, the close on the last trading day on or
              before the latest filing's reportperiod (10-day tolerance, read inside
              the factor from ctx.daily), the share count of the same filing.
              sharesbas is split-restated to today's basis and SEP.close is on the
              same basis; closeunadj is never used.
  Projection, OSAP's constants (autocorr_roe .57, cost_equity .12, autocorr_growth .24,
  longrun_growth .06), ten years:
    RoE_0 = ib / ceq_lag;  g_0 = sale / sale_lag - 1 (+-inf -> NaN, then NaN -> 0:
    OSAP's own `growth.fillna(0)`, reproduced, not a deviation).
    RoE_1 = .57 RoE_0 + .12 x .43;  RoE_t = .57 RoE_{t-1} + .12 x .43
    g_1   = .24 g_0 + .06 x .76;    g_t   = .24 g_{t-1} + .06 x .76
    BV_1 = ceq (1+g_1); CD_1 = ceq - BV_1 + ceq RoE_1
    BV_t = BV_{t-1}(1+g_t); CD_t = BV_{t-1} - BV_t + BV_{t-1} RoE_t
    MD = sum_t t CD_t / 1.12^t;  PV = sum_t CD_t / 1.12^t
    EquityDuration = MD/ME + (10 + 1.12/0.12)(1 - PV/ME)
  Raw, no log, no winsorising inside the factor (the harness's per-month 1/99 clip and
  within-sector rank absorb the tails). ascending=False: LOW duration is the long leg.

GUARDS:
  - ME > 0 (close > 0 and sharesbas > 0), else NaN.
  - ceq_lag == 0 -> NaN (OSAP would carry +-inf; +-inf is non-finite here).
  - NEGATIVE ceq_lag and ceq are KEPT, as OSAP does (no positive-book filter; RoE flips
    sign there; 2-5% of members). This is a deliberate exception to the usual
    "denominator > 0" guard: the spec reproduces OSAP's unfiltered sample.
  - fxusd != 1 -> NaN (USD cap over a reporting-currency numerator; non-USD reporters
    are 0.05-2.4% of members). Non-finite results -> NaN.
  - netinc, netincdis, equity, equity_lag, sharesbas, the period-end close missing -> NaN.
    Nothing is zero-filled except OSAP's own growth.fillna(0).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? There is no default value: the score is
  a continuous nonlinear function of RoE_0, g_0 and ceq/ME. A firm with no new filing
  repeats its inputs (ME is the period-end ME, fixed per filing), so its value is
  constant between filings: a cross-MONTH staleness, not a cross-sectional tie.
  What share of the universe does nothing? Not a tie block: the spec measured a modal
  share of 0.04-0.06% (1,700-2,300 distinct values) on the scratch replica; preflight
  measures it here. The risk is the tails (near-zero |ceq_lag| or ceq blow up), which
  are extreme values, not a mass.
  Tie handling: null (missing or non-finite input -> NaN, so blend_ranks renormalises).
  No zero-fill beyond OSAP's growth.fillna(0), no floor, no sample restriction.

DEVIATIONS FROM OSAP:
  - ceq -> SF1.equity (includes preferred; preferred not separable).
  - ib -> netinc + netincdis: continuing income after non-controlling interest; no
    separate extraordinary-items line, so any extraordinary item stays in.
  - Timing: ART at the latest filing (0-3 months old) and a quarterly update, vs OSAP's
    annual row at datadate + 6 months (6-17 months old), constant for 12 months. ib and
    revenue enter as TTM levels (a level over a level four quarters apart, no smear, no
    dimension override).
  - ceq_lag / sale_lag are strictly four quarters earlier by reportperiod (tol 45 days);
    OSAP takes the previous annual row, which can span a gap year.
  - ME is the period-end ME (close at the reportperiod, latest filing's sharesbas), not
    prcc_f x csho of a fiscal-year row; company-level cap.
  - The price read sits at the filing's own reportperiod (0-16 months back, a level read,
    not a return window), so no fixed history_months applies; a name with no period-end
    price within 10 days gets NaN.
  - Extra history: growth is NaN (then 0, OSAP's rule) when the year-ago revenue filing is
    missing; the spec measured 40-50% of scored names in 1999-H2 on this.
  - SignalDoc Filter is empty; OSAP's annual-pipeline drops (missing at/prcc_c/ni,
    curcd != USD) are represented by the NaN rules and the fxusd gate above.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_AUTOCORR_ROE = 0.57
_COST_EQUITY = 0.12
_AUTOCORR_G = 0.24
_LONGRUN_G = 0.06
_PRICE_TOL_DAYS = 10


def _period_end_close(ctx, reportperiod):
    """SEP.close on the last trading day on or before each ID's reportperiod,
    no more than _PRICE_TOL_DAYS earlier. Series indexed like `reportperiod`."""
    rp = pd.to_datetime(reportperiod).dropna()
    if rp.empty:
        return pd.Series(np.nan, index=reportperiod.index)
    days_back = int((ctx.signal_asof - rp.min()).days) + _PRICE_TOL_DAYS + 2
    d = ctx.daily("SEP", ["close"], days_back)
    if d.empty:
        return pd.Series(np.nan, index=reportperiod.index)
    d["ID"] = d["ID"].astype(str)
    d = d.dropna(subset=["close"]).sort_values("date", kind="mergesort")
    left = pd.DataFrame({"ID": rp.index.astype(str), "rp": rp.values}).sort_values("rp", kind="mergesort")
    got = pd.merge_asof(left, d[["ID", "date", "close"]], left_on="rp", right_on="date", by="ID",
                        direction="backward", tolerance=pd.Timedelta(days=_PRICE_TOL_DAYS))
    out = got.set_index("ID")["close"]
    out = out[~out.index.duplicated(keep="last")]
    return pd.Series(out.reindex(reportperiod.index.astype(str)).values, index=reportperiod.index, dtype=float)


def _compute(ctx):
    f = ctx.fundamentals_yoy(["netinc", "netincdis", "revenue", "equity", "sharesbas", "fxusd"])
    f = f.reindex(ctx.ids)

    ib = f["netinc"].astype(float) + f["netincdis"].astype(float)     # netincdis sign inverted: PLUS
    ceq = f["equity"].astype(float)
    ceq_lag = f["equity_lag"].astype(float)
    sale = f["revenue"].astype(float)
    sale_lag = f["revenue_lag"].astype(float)
    shares = f["sharesbas"].astype(float)
    usd = f["fxusd"].astype(float) == 1.0

    close = _period_end_close(ctx, f["reportperiod"])
    me = (close * shares).where((close > 0) & (shares > 0))

    roe0 = ib / ceq_lag.where(ceq_lag != 0)                            # negative book kept, as OSAP
    g0 = (sale / sale_lag.where(sale_lag != 0) - 1.0).replace([np.inf, -np.inf], np.nan).fillna(0.0)   # OSAP growth.fillna(0)

    roe_c = _COST_EQUITY * (1.0 - _AUTOCORR_ROE)
    g_c = _LONGRUN_G * (1.0 - _AUTOCORR_G)
    roe = _AUTOCORR_ROE * roe0 + roe_c
    g = _AUTOCORR_G * g0 + g_c
    bv = ceq * (1.0 + g)
    cd = ceq - bv + ceq * roe
    disc = 1.0 + _COST_EQUITY
    md = 1.0 * cd / disc
    pv = cd / disc
    for t in range(2, 11):
        roe = _AUTOCORR_ROE * roe + roe_c
        g = _AUTOCORR_G * g + g_c
        bv_new = bv * (1.0 + g)
        cd = bv - bv_new + bv * roe
        bv = bv_new
        md = md + t * cd / disc ** t
        pv = pv + cd / disc ** t

    dur = md / me + (10.0 + disc / _COST_EQUITY) * (1.0 - pv / me)
    dur = dur.where(usd)
    return dur.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EquityDuration",
    col="f_equityduration",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW duration is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.revenue", "SF1.equity", "SF1.sharesbas",
            "SF1.fxusd", "SEP.close"),
    osap_acronym="EquityDuration",
    source="Dechow, Sloan and Soliman 2004 (Review of Accounting Studies)",
    lookback_months=27,             # latest filing up to 15 months old + the year-ago filing 12 months earlier
    no_history_gate_because=("price read is the close at the latest filing's own reportperiod "
                             "(a level at a variable 0-16 month lag, with its own 10-day tolerance "
                             "inside the factor), not a return window; a missing period-end price "
                             "nulls the name"),
    notes="10-year ROE/growth projection of equity cash distributions; ART; ME = period-end SEP.close x sharesbas; sign -1",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ART)",
         "remap: the map's netinccmn is ibcom, not ib; netincdis sign inverted so PLUS; continuing income after NCI; extraordinary items not separable"),
        ("compustat.ceq (+ one-year lag)", "SF1.equity (ART), lag via fundamentals_yoy by reportperiod",
         "includes preferred; lag is strictly four quarters earlier, OSAP's is the previous annual row"),
        ("compustat.sale (+ one-year lag)", "SF1.revenue (ART TTM), lag via fundamentals_yoy",
         "NaN or inf growth -> 0 is OSAP's own growth.fillna(0), reproduced"),
        ("compustat.prcc_f x csho", "SEP.close at the latest filing's reportperiod (10-day tol) x SF1.sharesbas",
         "period-end ME of the latest filing, not a fiscal-year-end row; sharesbas split-restated, paired with split-adjusted close, never closeunadj; SF1.price (filing-date close) not used"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1"),
        ("timing", "ART latest filing (0-3 months old), quarterly update",
         "vs annual row at datadate + 6 months (6-17 months old), constant 12 months"),
        ("negative ceq / ceq_lag", "kept, as OSAP", "no positive-book filter; ceq_lag == 0 -> NaN"),
    ),
)
