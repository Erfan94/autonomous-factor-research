"""
THE COMPOSITE. Single source of truth for what the current alpha model is.

Every accepted factor is imported here from factors/accepted/, and
COMPOSITE_SHA (harness/provenance.py) is the hash of THIS file plus every
file it imports, in source order. Nothing else defines the composite — not
the registry (a log), not the manifest (a snapshot).

---------------------------------------------------------------------------
The search construction: a FAMILY blend
---------------------------------------------------------------------------
Every leg carries a `family`. The composite score is a two-level rank blend
(harness.analytics.blend_family_ranks): the mean of a name's available
member ranks within each family, then the mean across families. Equal
weight across families, equal weight within a family, no free parameter.
A new leg therefore dilutes only its own family, never the whole model,
which is what lets a signal be judged on the information it adds (Stage 2:
residual IC) rather than on whether one more equal vote can move a many-leg
average. How the legs are weighted for TRADING is Stage 3's report on
MODEL_MANIFEST.yaml, never a change here.

Families are assigned to Stage 1 passers by economic definition after the
screen and before any Stage 2 number exists (research/families.yaml logs
every assignment), fewer than ten in total. The five seeds below define the
first five.

---------------------------------------------------------------------------
Why the FF5 factors look different here than in Fama-French
---------------------------------------------------------------------------
Fama-French's SMB/HML/RMW/CMA are long-short PORTFOLIO RETURN SERIES. This
project scores individual stocks cross-sectionally and measures rank IC, so
the baseline is the STOCK-LEVEL characteristics those portfolios are built
from — small size, high book-to-market, high operating profitability, low
asset growth — plus 12-1 momentum, blended into one score.

MktRF is deliberately absent: a market-timing exposure with no cross-sectional
variation to rank on. The composite is a market-neutral cross-sectional score.
Every Sharadar-vs-Compustat deviation in a seed is in its field_mappings and
in osap_source/field_map.yaml.

---------------------------------------------------------------------------
How to add a factor (only after Stage 2 passes)
---------------------------------------------------------------------------
Move factors/candidates/<Name>.py to factors/accepted/<Name>.py (its
FactorDef already carries the family assigned before Stage 2), add
`from factors.accepted.<Name> import FACTOR as <NAME>` below, append <NAME>
to COMPOSITE_FACTORS with weight 1.0, bump COMPOSITE_VERSION. Never edit an
existing entry to "fix" a past composite — that rewrites history the
manifest claims to describe. Retire a factor by setting its weight to 0.0
and leaving the row.
"""

import numpy as np
import pandas as pd

from harness.analytics import family_members, family_weights
from harness.data_layer import to_bme
from harness.factor_def import FactorDef

# =============================================================================
# BASELINE — v0 composite (FF5 characteristics + momentum), one family each
# =============================================================================


def _size(ctx):
    # Small = attractive (SMB). Log first: raw market cap spans six orders of
    # magnitude; the rank is scale-free but log keeps every later transform
    # well-behaved. DAILY.marketcap as of the signal date, from the universe
    # frame — no extra read.
    mc = ctx.universe["mkt_cap_usd"].astype(float)
    return np.log(mc.where(mc > 0))


SIZE = FactorDef(
    name="Size", col="f_size", compute=_size,
    ascending=False,            # high market cap = BAD (large caps -> D1)
    weight=1.0,
    inputs=("DAILY.marketcap",),
    osap_acronym="Size", source="Fama-French SMB", family="size",
    notes="Reuses mkt_cap_usd from the universe frame.",
    field_mappings=(
        ("CRSP me (price x shares outstanding)", "DAILY.marketcap",
         "Sharadar's daily market cap uses the share count as of that date; "
         "CRSP me uses shares outstanding as reported that month."),),
)


def _value(ctx):
    # Book-to-market: SF1 equity (parent shareholders' equity, ART) over the
    # signal-date market cap. Negative book equity makes B/M meaningless
    # rather than merely extreme — a firm with -$1bn book and a $2bn market
    # cap would score as deep value — so those names get no Value score.
    f = ctx.fundamentals(["equity"])
    eq = f["equity"].astype(float)
    mc = ctx.universe["mkt_cap_usd"].astype(float)
    return eq.where(eq > 0) / mc.where(mc > 0)


VALUE = FactorDef(
    name="Value", col="f_value", compute=_value,
    ascending=True,             # high B/M = cheap = attractive
    weight=1.0,
    inputs=("SF1.equity", "DAILY.marketcap"),
    osap_acronym="BM", source="Fama-French HML", family="value",
    lookback_months=15,
    field_mappings=(
        ("Compustat ceq (+ txditc - pstk in BMdec) / CRSP me", "SF1.equity / DAILY.marketcap",
         "SF1 equity is parent equity with no preferred split and no deferred-tax "
         "add-back; OSAP's BM uses ceq. Sign and ordering agree; levels differ. "
         "Logged in field_map.yaml."),),
)


def _profitability(ctx):
    # FF RMW numerator = revenue - COGS - SG&A - interest expense, over book
    # equity. Compustat xsga INCLUDES R&D; Sharadar breaks rnd out of sgna, so
    # both are subtracted. FF's rule: revenue and COGS present, and at least
    # one of the three expense items non-missing (missing ones count as zero).
    f = ctx.fundamentals(["revenue", "cor", "sgna", "rnd", "intexp", "equity"])
    rev, cor = f["revenue"].astype(float), f["cor"].astype(float)
    exp = f[["sgna", "rnd", "intexp"]].astype(float)
    ok = rev.notna() & cor.notna() & exp.notna().any(axis=1)
    num = (rev - cor - exp.fillna(0.0).sum(axis=1)).where(ok)
    den = f["equity"].astype(float)
    # Negative book equity flips the ratio's sign and would rank a loss-making,
    # balance-sheet-impaired firm as highly profitable. Guard, don't clip.
    return num / den.where(den > 0)


PROFITABILITY = FactorDef(
    name="Profitability", col="f_prof", compute=_profitability,
    ascending=True,             # robust profitability = attractive
    weight=1.0,
    inputs=("SF1.revenue", "SF1.cor", "SF1.sgna", "SF1.rnd", "SF1.intexp", "SF1.equity"),
    osap_acronym="OperProf", source="Fama-French RMW", family="profitability",
    lookback_months=15,
    notes=("Built from the literal components, which SF1 carries for every filer "
           "including banks (intexp is populated for financials in SF1), so the "
           "leg has no structural Financials hole."),
    field_mappings=(
        ("Compustat revt - cogs - xsga - xint over ceq",
         "(revenue - cor - (sgna + rnd) - intexp) / equity, ART",
         "xsga includes R&D in Compustat; SF1 splits rnd out, so both are "
         "subtracted. Missing expense items are zero-filled if at least one is "
         "present (FF convention). Trailing-twelve-month figures as of the "
         "filing date rather than fiscal-year figures aligned to June."),),
)


def _investment(ctx):
    # Asset growth: latest total assets known at the signal date over the
    # latest known 12 months earlier. The lagged leg is looked up with its OWN
    # as-of date (datekey <= signal - 12m), never "the figure for the earlier
    # period as known today" — that would be the restated number.
    a0 = ctx.fundamentals(["assets"])["assets"].astype(float)
    a1 = ctx.fundamentals(["assets"], lag_months=12)["assets"].astype(float)
    return a0 / a1.where(a1 > 0) - 1.0


INVESTMENT = FactorDef(
    name="Investment", col="f_inv", compute=_investment,
    ascending=False,            # high asset growth = BAD (conservative = attractive)
    weight=1.0,
    inputs=("SF1.assets",),
    osap_acronym="AssetGrowth", source="Fama-French CMA", family="investment",
    lookback_months=27,
    field_mappings=(
        ("Compustat at / lagged at", "SF1.assets (ART) at two as-of dates",
         "OSAP lags by fiscal year with a reporting gap; here the lag is 12 "
         "calendar months of KNOWN data. Post-ASC-842 operating-lease assets are "
         "on the balance sheet from 2019, a real jump in reported assets for "
         "lease-heavy sectors with nothing to do with investment."),),
)


def _momentum(ctx):
    # 12-1 momentum from split- and dividend-adjusted closes at business
    # month-ends: closeadj(signal - 1m) / closeadj(signal - 12m) - 1. The
    # most recent month is skipped to avoid short-term reversal. history_months
    # = 12 makes the harness null this leg for any name without a trade near
    # the window start, so it never scores a name that did not exist.
    px = ctx.monthly_closeadj(12)
    asof = ctx.signal_asof
    end = to_bme([(asof - pd.DateOffset(months=1)).normalize()]).iloc[0]
    start = to_bme([(asof - pd.DateOffset(months=12)).normalize()]).iloc[0]
    if end not in px.columns or start not in px.columns:
        return pd.Series(np.nan, index=ctx.ids)
    p_end, p_start = px[end].astype(float), px[start].astype(float)
    return p_end / p_start.where(p_start > 0) - 1.0


MOMENTUM = FactorDef(
    name="Momentum", col="f_mom", compute=_momentum,
    ascending=True,             # past winners = attractive
    weight=1.0,
    inputs=("SEP.closeadj",),
    history_months=12,
    lookback_months=12,
    osap_acronym="Mom12m", source="Carhart / Jegadeesh-Titman", family="momentum",
    field_mappings=(
        ("CRSP ret, cumulated t-12..t-2", "SEP.closeadj ratio over [-12M, -1M] month-ends",
         "closeadj is split- and dividend-adjusted, so the ratio is a total "
         "return; CRSP compounds monthly holding-period returns. Month-end to "
         "month-end rather than OSAP's calendar-month cumulation."),),
)


# =============================================================================
# ACCEPTED FROM THE SEARCH — appended below in acceptance order, never edited
# =============================================================================

# (none yet — the search starts from v0)

COMPOSITE_FACTORS = [SIZE, VALUE, PROFITABILITY, INVESTMENT, MOMENTUM]

# Model version this file currently represents. factor-evaluator bumps it when
# a factor is accepted, and MODEL_MANIFEST.yaml must gain a matching block.
COMPOSITE_VERSION = "v0"


def active_factors():
    """Factors with a positive weight — what the composite actually is now."""
    return [f for f in COMPOSITE_FACTORS if f.weight > 0]


def families():
    """family -> [leg names] of the live composite, in source order."""
    return family_members([f.meta() for f in active_factors()])


def weights():
    """The search construction as flat per-leg weights: 1/F per family, split
    equally within. (The score itself is the two-level blend; these are the
    weights it reduces to when every leg is available.)"""
    act = active_factors()
    if not act:
        raise ValueError("Composite has no positively-weighted factors.")
    return family_weights([f.meta() for f in act])


def weights_with(candidate):
    """Family weights for the composite PLUS one candidate, which must carry
    a family (assigned before Stage 2)."""
    act = active_factors()
    if any(f.name == candidate.name for f in act):
        raise ValueError(f"{candidate.name} is already in the composite.")
    if candidate.family is None:
        raise ValueError(f"{candidate.name} has no family; assign one before Stage 2.")
    return family_weights([f.meta() for f in act] + [candidate.meta()])
