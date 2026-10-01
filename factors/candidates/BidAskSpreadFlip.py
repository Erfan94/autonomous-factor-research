"""
BidAskSpreadFlip — the declared second hypothesis on BidAskSpread: the same
Corwin-Schultz monthly spread, oriented AGAINST OSAP's published sign (narrow
spread in D10). Qualified by run 003 (BidAskSpread NW IC t -2.77, |t| >= 2.74,
event flip_hypothesis_qualified). Stage 1 bar for this file: NW IC t >= 2.74
(not 2.5), and its registry row carries the flipped-sign caveat.
Construction identical to BidAskSpread.py (copied below); only name, col and
ascending differ.

BidAskSpread — Corwin-Schultz (2011) high-low estimate of the effective
bid-ask spread, averaged over the signal month; a wide spread marks an illiquid
stock, and illiquidity is predicted to be compensated with a higher return.

OSAP: BidAskSpread, Amihud and Mendelson 1986, Journal of Financial Economics
(Table 2 "Spread Mean"; OSAP builds it with the Corwin-Schultz program).
Predicted sign: + (high spread earns higher returns).
Spec: osap_source/cache/b4e911e6/BidAskSpread/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Daily rows of SEP (high, low, close, volume) for the universe, in date order
  per ID, run through the program's recursion:
  1. Screen: low == high, low <= 0, high <= 0, close <= 0 or volume == 0 ->
     the day's low/high are set missing.
  2. Retained range: a day with 0 < low < high becomes the retained range. A
     screened day is filled from the retained range of the last good day:
     close inside it -> copy it; close below -> low = close, high = retained
     high - (retained low - close); close above -> high = close, low =
     retained low + (close - retained high). No retained range yet -> stays
     missing (not zero-filled).
  3. Drop the day if high/low > 8.
  4. Overnight adjustment against the previous row's close (same ID): close
     below today's low -> high lowered by the gap, low = close; close above
     today's high -> high = close, low raised by the gap.
  5. beta = ln(thi/tlo)^2 + ln(prev hi/prev lo)^2 (prev = previous row's
     post-fill range); gamma = ln(max(thi, prev hi)/min(tlo, prev lo))^2;
     alpha = (sqrt(2 beta) - sqrt(beta))/(3 - 2 sqrt 2) - sqrt(gamma/(3 - 2 sqrt 2));
     spread = 2 (e^alpha - 1)/(1 + e^alpha) (written 2 tanh(alpha/2), the same
     number); daily value = max(spread, 0), a missing spread stays missing.
  6. Only rows in the calendar month that ends at the signal date are scored.
     N = count of non-missing daily spreads; N < 12 -> NaN; otherwise the value
     is the plain mean of the daily values (negatives already set to zero before
     averaging). A fraction of price (round trip); no further scaling.
  Timing: the estimate for calendar month m is available at the month-end
  signal date of m, as in OSAP (stamped m, portfolio earns m+1). No filing
  data, so no dimension and no lag question.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A day with volume == 0 or
  high == low is screened, then REPLACED by the retained range (CRSP's
  negative-price / quote-flag days are the screened equivalent; here volume == 0
  is the only flag, high == low the other trigger). It is neither zero-filled
  nor dropped, so a no-trade day adds a positive-range estimate. A name
  produces exactly 0.0 only if all of >= 12 daily estimates in the month are
  <= 0 (roughly 30% of single days are negative); a name with < 12
  non-missing days (never a good range yet, or dead-traded) is NaN, not 0.
  What share of the universe does nothing? Expected exact-zero share ~0.0%
  (scratch check in the spec on price >= $1 names: 0.0% in three months; the
  relative liquidity band removes nearly all no-trade names) and N < 12 about
  0.6-0.8% of price >= $1 names, fewer inside the band. Preflight decides.
  Tie handling: none needed, kept as measured. A monthly mean of exactly 0 is
  a real measurement (every day's estimate non-positive, i.e. a spread not
  distinguishable from zero), and nulling it would delete the most liquid
  names from D1 selectively, so it is left in and ties average-ranked. The
  N >= 12 rule is the null (renormalised by blend_ranks). If preflight shows
  a mode >= 10%, the design is to be revisited, not patched here.

DEVIATIONS FROM OSAP:
  - prc / bidlo / askhi: SEP.close / low / high are split-adjusted on one basis;
    CRSP dsf is not. OSAP's split-day discontinuity and the spurious range it
    creates do not arise here, so split-day estimates differ (rare).
  - no-trade flag: CRSP negative prc / negative bid-ask on no-trade days do not
    exist in SEP; volume == 0 replaces them (98.5% of volume == 0 rows also have
    high == low, so the screen fires on them either way). close <= 0 never fires.
  - retained-range seed: OSAP retains the range from the start of each permno's
    history; here the recursion starts at the first row of a fixed 125 calendar
    day window (about 4 months). A name with no good range in the window, or
    with fewer than 3 months of history (history gate), is unscored.
  - vendor: SEP daily high/low extrema can differ slightly from CRSP's.
  - the snapshot's first month (1997-12, a one-day stub) is never scored.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_DAYS_BACK = 125        # target month (<= 31 days) + ~94 days of range / lag warm-up
_MIN_DAYS = 12          # N >= 12 valid daily estimates in the month
_C = 3.0 - 2.0 * np.sqrt(2.0)


def _daily_spread(df):
    """Daily spread_0 for rows sorted by (ID, date): the vectorised form of the
    Corwin-Schultz program. `df` has ID, high, low, close, volume."""
    g = df["ID"].to_numpy()
    hi = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    px = df["close"].to_numpy(dtype=float)
    vol = df["volume"].to_numpy(dtype=float)

    with np.errstate(invalid="ignore", divide="ignore"):
        # 1. screen
        bad = (lo == hi) | (lo <= 0) | (hi <= 0) | (px <= 0) | (vol == 0)
        lo1 = np.where(bad, np.nan, lo)
        hi1 = np.where(bad, np.nan, hi)

        # 2. retained range = last good range at or before the row, per ID
        good = (lo1 > 0) & (lo1 < hi1)
        ret = pd.DataFrame({"g": g, "lo": np.where(good, lo1, np.nan),
                            "hi": np.where(good, hi1, np.nan)})
        rlo = ret.groupby("g")["lo"].ffill().to_numpy()
        rhi = ret.groupby("g")["hi"].ffill().to_numpy()
        within = (rlo <= px) & (px <= rhi)
        below = px < rlo
        above = px > rhi
        lo2 = np.where(good, lo1, np.where(within, rlo, np.where(below, px, np.where(above, rlo + (px - rhi), np.nan))))
        hi2 = np.where(good, hi1, np.where(within, rhi, np.where(below, rhi - (rlo - px), np.where(above, px, np.nan))))

        # 3. high/low > 8 is dropped
        drop = (lo2 != 0) & (hi2 / lo2 > 8)
        lo2 = np.where(drop, np.nan, lo2)
        hi2 = np.where(drop, np.nan, hi2)

        # 4. overnight adjustment; lags are the previous row of the same ID
        pr = pd.DataFrame({"g": g, "lo": lo2, "hi": hi2, "px": px})
        sh = pr.groupby("g")[["lo", "hi", "px"]].shift(1)
        llo, lhi, lpx = sh["lo"].to_numpy(), sh["hi"].to_numpy(), sh["px"].to_numpy()
        c1 = (lpx < lo2) & (lpx > 0)
        c2 = (lpx > hi2) & (lpx > 0)
        thi = np.where(c2, lpx, np.where(c1, hi2 - (lo2 - lpx), hi2))
        tlo = np.where(c2, lo2 + (lpx - hi2), np.where(c1, lpx, lo2))

        # 5. beta, gamma, alpha, spread
        ok = (tlo > 0) & (llo > 0) & (thi > 0) & (lhi > 0)
        beta = np.where(ok, np.log(thi / tlo) ** 2 + np.log(lhi / llo) ** 2, np.nan)
        hi_2 = np.maximum(thi, lhi)
        lo_2 = np.minimum(tlo, llo)
        gamma = np.where(lo_2 > 0, np.log(hi_2 / lo_2) ** 2, np.nan)
        alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / _C - np.sqrt(gamma / _C)
        spread = 2.0 * np.tanh(alpha / 2.0)          # = 2(e^a - 1)/(1 + e^a)
        spread0 = np.where(np.isfinite(spread), np.maximum(spread, 0.0), np.nan)
    return spread0


def _compute(ctx):
    month = ctx.signal_asof.to_period("M")
    if month in ctx.partial_months("SEP"):
        return pd.Series(dtype=float)
    d = ctx.daily("SEP", ["high", "low", "close", "volume"], _DAYS_BACK)
    if d.empty:
        return pd.Series(dtype=float)
    d = d.sort_values(["ID", "date"], kind="mergesort").reset_index(drop=True)
    d["s0"] = _daily_spread(d)

    cur = d[(d["date"].dt.to_period("M") == month) & d["s0"].notna()]
    grp = cur.groupby("ID")["s0"]
    n = grp.count()
    mean = grp.mean()
    return mean.where(n >= _MIN_DAYS)


FACTOR = FactorDef(
    family="liquidity",                # Phase C, 2026-10-01: Cat.Economic "liquidity" (decision phase_c_family_partition)
    name="BidAskSpreadFlip",
    col="f_bidaskspreadflip",
    compute=_compute,
    ascending=False,                # FLIPPED vs SignalDoc Sign +1: second hypothesis, narrow spread in D10
    weight=1.0,
    inputs=("SEP.high", "SEP.low", "SEP.close", "SEP.volume"),
    osap_acronym="BidAskSpread",
    source="Amihud and Mendelson 1986 (Journal of Financial Economics)",
    lookback_months=4,              # signal month plus ~94 days of warm-up (125 calendar days)
    history_months=3,               # daily-price history gate, per the spec
    notes="FLIPPED second hypothesis (|t| >= 2.74 bar); Corwin-Schultz daily high-low spread, negatives to 0, mean over the signal month, N >= 12 valid days",
    field_mappings=(
        ("crsp.askhi", "SEP.high", "split-adjusted on the same basis as close; CRSP dsf is unadjusted (no split-day artefact here)"),
        ("crsp.bidlo", "SEP.low", "split-adjusted on the same basis as close; vendor extrema may differ slightly"),
        ("crsp.prc", "SEP.close", "positive always; CRSP negative-price quote flag does not exist, so prc<=0 never fires"),
        ("crsp.vol", "SEP.volume", "volume==0 is the only no-trade flag (replaces CRSP negative prc / bid-ask on no-trade days)"),
        ("retained range", "125-calendar-day window of SEP rows", "OSAP retains from each permno's first row; seed here is the window start, so names with no good range in ~4 months are unscored"),
    ),
)
