"""
The factor contract: what a `.factor.py` may say, and nothing else.

A factor is a function from one month's point-in-time context to one Series
of raw signal values indexed by ID. Universe, dates, rebalancing, winsorising,
ranking, deciles, IC, long-short economics and the report all belong to the
harness and are byte-identical for every factor. A factor file that contains
any of those has been tested under different conditions from the rest of the
registry, and the comparison is the only reason this project exists.

Why callables rather than source text: the BQuant project stored `items_code`
and `derive_code` as STRINGS because they were emitted into a generated cell
that ran on Bloomberg's servers. Nothing here runs anywhere but this machine,
so a factor is ordinary Python. What is kept is the provenance property: the
composite hash covers the BYTES of every accepted factor file
(harness/provenance.py), so the composite's behaviour is still visible in the
hashed text.
"""

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

# Inputs are declared as "TABLE.field" strings. preflight.py checks every one
# against the snapshot manifest and the on-disk schema BEFORE a run, which
# replaces the BQuant project's help-centre lookups with a check against the
# actual bytes. A field that exists but means something different is still
# the translator's problem; a field that does not exist never reaches a run.
VALID_TABLES = {"SEP", "SF1", "DAILY", "TICKERS", "ACTIONS", "EVENTS",
                "SF2", "SF3", "SP500", "METRICS"}

VALID_DIMENSIONS = {"ARQ", "ARY", "ART", "MRQ", "MRY", "MRT"}


@dataclass(frozen=True)
class FactorDef:
    """One stock-level signal.

    name         — registry name, e.g. "Accruals".
    col          — the audit-frame column, e.g. "f_accruals". Must be unique
                   across the composite and every candidate in a batch.
    compute      — callable(ctx) -> pd.Series indexed by ID. `ctx` is a
                   harness.data_layer.MonthContext: it exposes the universe
                   frame, point-in-time fundamentals (latest filing on or
                   before the signal date, optionally lagged), monthly and
                   daily price history, and nothing dated after the signal.
    ascending    — True when a HIGH raw value is attractive (D10).
    weight       — 1.0 in the composite; 0.0 retires a leg without deleting
                   its row.
    inputs       — every "TABLE.field" the compute function reads. Declared,
                   not inferred, so preflight can verify them and so the
                   registry row records what the factor consumed.
    dimension    — SF1 dimension for THIS factor's fundamentals when the
                   project default (config point_in_time.sf1_dimension) would
                   make it WRONG rather than merely different — a quarterly
                   flow (ARQ) or a fiscal-year figure (ARY). None means the
                   default. Non-default values are printed in the run header
                   and carried into the result block as `dimension_overrides`,
                   so a row measured under a different dimension says so.
                   CONFIG_SHA does not move; the record is what makes it
                   visible. The BQuant project's `pit_overrides`, one field.
    history_months — REQUIRED for any signal built from a return window. The
                   harness nulls the factor for any name without a price
                   within 7 calendar days of (signal date - N months), so the
                   leg never scores a name that did not exist over its window.
                   An earlier search accepted legs against a Momentum leg
                   that did, and had to re-run its whole ladder; the
                   gate is built in here from day one, and the harness
                   REFUSES a factor whose inputs include SEP prices and whose
                   history_months is None unless it also sets
                   `no_history_gate_because`.
    lookback_months — how far back the signal reaches, for the data-start
                   check: a snapshot beginning 1998-01 cannot score a 60-month
                   window at the 1999-01 rebalance, and preflight says so
                   before the run rather than the coverage table after it.
    no_history_gate_because — the stated reason a price-based factor needs no
                   gate (e.g. it uses only the signal-date price).
    family       — the economic family this signal belongs to in the
                   composite. The SEARCH construction is a family blend:
                   equal weight across families, equal weight within a
                   family (harness.analytics.family_weights). A family is
                   assigned after Stage 1 and before any Stage 2 number
                   exists, never changed afterwards; it is REQUIRED on every
                   composite leg and on every Stage 2 candidate, and None on
                   a Stage 1 candidate (screened alone). Lower-case slug.
    """
    name: str
    col: str
    compute: Callable
    ascending: bool
    weight: float
    inputs: tuple = ()
    osap_acronym: Optional[str] = None
    source: str = ""
    winsorize: bool = True
    notes: str = ""
    field_mappings: tuple = field(default_factory=tuple)
    dimension: Optional[str] = None
    history_months: Optional[int] = None
    lookback_months: int = 0
    no_history_gate_because: str = ""
    family: Optional[str] = None

    def validate(self):
        """Structural checks that cost nothing and catch the cheap mistakes."""
        problems = []
        if not self.col.startswith("f_"):
            problems.append(f"{self.name}: col must start with 'f_' (got {self.col!r})")
        if not callable(self.compute):
            problems.append(f"{self.name}: compute is not callable")
        for inp in self.inputs:
            if "." not in inp or inp.split(".", 1)[0] not in VALID_TABLES:
                problems.append(f"{self.name}: input {inp!r} is not TABLE.field "
                                f"with TABLE in {sorted(VALID_TABLES)}")
        if self.dimension is not None and self.dimension not in VALID_DIMENSIONS:
            problems.append(f"{self.name}: dimension {self.dimension!r} not in "
                            f"{sorted(VALID_DIMENSIONS)}")
        uses_prices = any(i.startswith("SEP.") for i in self.inputs)
        if uses_prices and self.history_months is None and not self.no_history_gate_because:
            problems.append(
                f"{self.name}: reads SEP prices but declares no history_months and "
                "no no_history_gate_because. A return-window factor without a "
                "history gate scores names that did not exist.")
        if self.family is not None and not re.fullmatch(r"[a-z][a-z0-9_]*", self.family):
            problems.append(f"{self.name}: family {self.family!r} must be a lower-case slug")
        if self.history_months is not None and self.lookback_months < self.history_months:
            problems.append(f"{self.name}: lookback_months ({self.lookback_months}) "
                            f"< history_months ({self.history_months})")
        return problems

    def meta(self):
        """The dict analytics.py works with. Kept tiny on purpose."""
        return {"name": self.name, "col": self.col, "ascending": self.ascending,
                "winsorize": self.winsorize, "weight": float(self.weight),
                "family": self.family}
