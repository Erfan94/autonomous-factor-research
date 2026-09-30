import pandas as pd

from harness.data_layer import MonthContext


class _Snap:
    def __init__(self, dates):
        self._d = pd.DataFrame({"date": pd.to_datetime(dates)})
        self.calls = 0

    def table(self, name, columns=None, keep=True):
        self.calls += 1
        return self._d


def _ctx(snap):
    ctx = MonthContext.__new__(MonthContext)
    ctx.snap = snap
    return ctx


def test_mid_month_start_is_a_partial_month():
    snap = _Snap(["1997-12-31", "1998-01-02", "1998-01-05"])
    assert _ctx(snap).partial_months("SEP") == frozenset({pd.Period("1997-12", "M")})


def test_first_business_day_start_is_not_partial():
    # 1998-02-02 is the first business day of February 1998 (Feb 1 is a Sunday)
    snap = _Snap(["1998-02-02", "1998-02-03"])
    assert _ctx(snap).partial_months("SEP") == frozenset()


def test_computed_once_per_snapshot_and_table():
    snap = _Snap(["1997-12-31", "1998-01-02"])
    ctx = _ctx(snap)
    ctx.partial_months("SEP")
    ctx.partial_months("SEP")
    _ctx(snap).partial_months("SEP")
    assert snap.calls == 1
