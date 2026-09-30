"""Industry adjustment for a signal value (HX-2).

The primitive exists so that OSAP's industry-adjusted predictors (ChInvIA,
EarnSupBig, IndMom, iomom_*) can be expressed without each factor file
improvising its own cross-sectional group logic — and so that the deviation it
carries (current vendor SIC, peers restricted to the screened universe) is
hashed into HARNESS_SHA once, where a reader can find it.
"""
import numpy as np
import pandas as pd
import pytest

from harness.industry import (MIN_GROUP_FOR_DEMEAN, ff17, ff48, get_ff48, group_demean,
                              group_mean_where, group_zscore, sic_group)


def _v(vals, idx=None):
    return pd.Series(vals, index=idx or list("abcdefghij")[: len(vals)], dtype="float64")


def test_sic_group_takes_leading_digits():
    s = sic_group(pd.Series([2011, 7372, 100, 9999]))
    assert list(s) == [20.0, 73.0, 1.0, 99.0]
    assert list(sic_group(pd.Series([2011, 7372]), digits=3)) == [201.0, 737.0]


def test_sic_group_is_nan_for_missing_or_unparseable():
    s = sic_group(pd.Series([2011, None, "not a code", np.nan]))
    assert s.notna().tolist() == [True, False, False, False]


def test_sic_group_rejects_a_digit_count_that_is_not_a_sic_prefix():
    with pytest.raises(ValueError):
        sic_group(pd.Series([2011]), digits=5)


def test_group_demean_subtracts_the_within_group_mean():
    v = _v([1, 2, 3, 4, 5, 6])
    g = pd.Series([10] * 6, index=v.index)
    out = group_demean(v, g)
    assert out.tolist() == pytest.approx([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
    assert out.sum() == pytest.approx(0.0)


def test_group_demean_is_independent_across_groups():
    v = _v([1, 2, 3, 4, 5, 101, 102, 103, 104, 105])
    g = pd.Series([1] * 5 + [2] * 5, index=v.index)
    out = group_demean(v, g)
    assert out.tolist() == pytest.approx([-2, -1, 0, 1, 2, -2, -1, 0, 1, 2])


def test_group_demean_nulls_a_group_below_the_size_floor():
    """A two-firm industry would hand each firm the negative of the other —
    noise wearing a signal's clothes. It must come back NaN, not 0."""
    v = _v([1, 2, 3, 4, 5, 6, 10, 20])
    g = pd.Series([1] * 6 + [2, 2], index=v.index)
    out = group_demean(v, g)
    assert out[:6].notna().all()
    assert out[6:].isna().all()


def test_group_demean_size_floor_counts_non_null_values_only():
    v = _v([1, 2, 3, np.nan, np.nan, np.nan])
    g = pd.Series([7] * 6, index=v.index)
    assert group_demean(v, g).isna().all(), "3 real values must not clear a floor of 5"


def test_group_demean_nulls_rows_with_no_industry():
    v = _v([1, 2, 3, 4, 5, 6])
    g = pd.Series([1, 1, 1, 1, 1, np.nan], index=v.index)
    out = group_demean(v, g)
    assert np.isnan(out.iloc[5])
    assert out.iloc[:5].tolist() == pytest.approx([-2, -1, 0, 1, 2])


def test_group_demean_preserves_the_input_index_and_length():
    v = _v([1, 2, 3, 4, 5, 6, 7])
    g = pd.Series([1] * 7, index=v.index)
    out = group_demean(v, g)
    assert out.index.equals(v.index) and len(out) == len(v)


def test_group_demean_is_all_nan_when_nothing_is_scoreable():
    v = _v([np.nan, np.nan, np.nan])
    g = pd.Series([1, 1, 1], index=v.index)
    assert group_demean(v, g).isna().all()


def test_group_demean_uses_only_the_month_it_is_given():
    """Cross-sectional by construction: the caller passes one month, so a
    later month's values cannot reach the mean. Demeaning a month in isolation
    and as part of a two-month concat must agree."""
    idx = list("abcdef")
    m1 = pd.Series([1.0, 2, 3, 4, 5, 6], index=idx)
    g = pd.Series([1] * 6, index=idx)
    alone = group_demean(m1, g)
    m2 = pd.Series([100.0, 200, 300, 400, 500, 600], index=idx)
    together = group_demean(m2, g)
    assert alone.tolist() == pytest.approx([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
    assert together.tolist() == pytest.approx([-250, -150, -50, 50, 150, 250])


def test_min_group_floor_is_declared_not_magic():
    assert MIN_GROUP_FOR_DEMEAN >= 2


def test_ff17_and_sic_group_answer_different_questions():
    sic = pd.Series([2011, 2013])
    assert ff17(sic).nunique() == 1
    assert sic_group(sic).nunique() == 1
    tech, food = pd.Series([7372]), pd.Series([2011])
    assert ff17(tech).iloc[0] != ff17(food).iloc[0]


def test_group_zscore_standardises_within_group():
    v = _v([1, 2, 3, 4, 5, 6])
    g = pd.Series([10] * 6, index=v.index)
    out = group_zscore(v, g, winsor=None)
    expected = (v - v.mean()) / v.std(ddof=1)
    assert out.tolist() == pytest.approx(expected.tolist())
    assert out.mean() == pytest.approx(0.0)
    assert out.std(ddof=1) == pytest.approx(1.0)


def test_group_zscore_is_independent_across_groups():
    v = _v([1, 2, 3, 4, 5, 101, 102, 103, 104, 105])
    g = pd.Series([1] * 5 + [2] * 5, index=v.index)
    out = group_zscore(v, g, winsor=None)
    z = np.array([-2, -1, 0, 1, 2]) / np.std([1, 2, 3, 4, 5], ddof=1)
    assert out.tolist() == pytest.approx(list(z) * 2)


def test_group_zscore_nulls_a_group_below_the_size_floor():
    v = _v([1, 2, 3, 4, 5, 6, 10, 20])
    g = pd.Series([1] * 6 + [2, 2], index=v.index)
    out = group_zscore(v, g)
    assert out[:6].notna().all()
    assert out[6:].isna().all()


def test_group_zscore_size_floor_counts_non_null_values_only():
    v = _v([1, 2, 3, np.nan, np.nan, np.nan])
    g = pd.Series([7] * 6, index=v.index)
    assert group_zscore(v, g).isna().all()


def test_group_zscore_nulls_a_zero_std_group():
    v = _v([3, 3, 3, 3, 3, 1, 2, 3, 4, 5])
    g = pd.Series([1] * 5 + [2] * 5, index=v.index)
    out = group_zscore(v, g, winsor=None)
    assert out[:5].isna().all()
    assert out[5:].notna().all()


def test_group_zscore_nulls_rows_with_no_industry():
    v = _v([1, 2, 3, 4, 5, 6])
    g = pd.Series([1, 1, 1, 1, 1, np.nan], index=v.index)
    out = group_zscore(v, g, winsor=None)
    assert np.isnan(out.iloc[5])
    assert out.iloc[:5].notna().all()


def test_group_zscore_preserves_the_input_index_and_length():
    v = _v([1, 2, 3, 4, 5, 6, 7])
    g = pd.Series([1] * 7, index=v.index)
    out = group_zscore(v, g)
    assert out.index.equals(v.index) and len(out) == len(v)


def test_group_zscore_is_all_nan_when_nothing_is_scoreable():
    v = _v([np.nan, np.nan, np.nan])
    g = pd.Series([1, 1, 1], index=v.index)
    assert group_zscore(v, g).isna().all()


def test_group_zscore_winsorises_cross_sectionally_like_osap():
    """OSAP OrgCap predictor.py:106-123 clips at np.percentile(1, 'lower') /
    np.percentile(99, 'higher') over the whole month, before industry cells
    exist — so a null-group name still sets the bounds, and the clip is not
    within-group."""
    idx = [f"n{i}" for i in range(200)]
    rng = np.random.default_rng(0)
    raw = pd.Series(rng.normal(size=200), index=idx)
    raw.iloc[0] = 1e6            # outlier in group 1
    raw.iloc[-1] = -1e6          # outlier with no group: still in the clip sample
    g = pd.Series([1] * 100 + [2] * 99 + [np.nan], index=idx)
    lo = np.percentile(raw.to_numpy(), 1, method="lower")
    hi = np.percentile(raw.to_numpy(), 99, method="higher")
    w = raw.clip(lo, hi)
    expected = pd.Series(np.nan, index=idx)
    for k in (1, 2):
        m = g == k
        expected[m] = (w[m] - w[m].mean()) / w[m].std(ddof=1)
    out = group_zscore(raw, g)
    assert out.tolist() == pytest.approx(expected.tolist(), nan_ok=True)
    assert np.isnan(out.iloc[-1])
    # Group-1 bounds would differ from the pooled bounds: the clip is pooled.
    lo1 = np.percentile(raw[g == 1].to_numpy(), 1, method="lower")
    assert lo1 != lo


def test_group_zscore_winsor_none_leaves_values_unclipped():
    v = _v([1, 2, 3, 4, 1000])
    g = pd.Series([1] * 5, index=v.index)
    a = group_zscore(v, g, winsor=None)
    b = group_zscore(v, g)
    assert a.tolist() == pytest.approx(((v - v.mean()) / v.std(ddof=1)).tolist())
    assert a.notna().all() and b.notna().all()


# ---- FF48 (verbatim OSAP sicff.py::get_ff48 at b4e911e6) ---------------------

@pytest.mark.parametrize("sic, want", [
    (7372, 34),     # prepackaged software: FF48 34 Business Services (7370-7372)
    (7373, 35),     # computer integrated systems design: 35 Computers
    (6022, 44),     # state commercial banks: 44 Banking
    (6798, 47),     # REITs: 47 Trading
    (4911, 31),     # electric services: 31 Utilities
    (2834, 13),     # pharmaceutical preparations: 13 Pharmaceutical Products
    (2836, 13),     # biological products: 13
    (1311, 30),     # crude petroleum & natural gas: 30
    (5812, 43),     # eating places: 43 Restaurants, Hotels, Motels
    (3674, 36),     # semiconductors: 36 Electronic Equipment
    (6311, 45),     # life insurance: 45 Insurance
    (100, 1),       # agriculture: 1
    (4991, 48),     # 48 Almost Nothing (4990-4991)
])
def test_ff48_known_assignments(sic, want):
    assert get_ff48(sic) == want
    assert get_ff48(float(sic)) == want            # a float SIC from parquet
    assert get_ff48(str(sic)) == want              # int() of a numeric string, as upstream


@pytest.mark.parametrize("sic", [None, np.nan, "not a code", 9100, 9999, 6780, 6797])
def test_ff48_is_nan_for_missing_or_unlisted(sic):
    assert np.isnan(get_ff48(sic))


def test_ff48_series_wrapper_mirrors_ff17():
    s = ff48(pd.Series([7372, None, 6022, 9999], index=list("abcd")))
    assert list(s.index) == list("abcd")
    assert s.iloc[0] == 34 and s.iloc[2] == 44
    assert s.iloc[[1, 3]].isna().all()
    assert set(ff48(pd.Series(range(0, 10000))).dropna().unique()) == set(range(1, 49))


def test_ff48_is_the_pinned_upstream_source_verbatim():
    """The table is behaviour hashed into HARNESS_SHA; it must be OSAP's own
    text at b4e911e6, not a retyped copy."""
    import inspect
    from harness.provenance import ROOT
    up = (ROOT / "osap_source" / "cache" / "b4e911e6" / "IndRetBig" / "upstream_sicff.py").read_text()
    assert inspect.getsource(get_ff48).rstrip("\n") in up


# ---- group_mean_where (EarnSupBig's member-mean broadcast) ------------------

def test_group_mean_where_broadcasts_member_mean_to_everyone():
    v = _v([10, 20, 30, 1, 2, 3])
    g = pd.Series([1] * 6, index=v.index)
    member = pd.Series([True, True, True, False, False, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=3)
    assert out.tolist() == pytest.approx([20.0] * 6)


def test_group_mean_where_ignores_non_member_values_in_the_mean():
    v = _v([10, 20, 1000, 1, 2])
    g = pd.Series([1] * 5, index=v.index)
    member = pd.Series([True, True, False, False, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=2)
    assert out.tolist() == pytest.approx([15.0] * 5)


def test_group_mean_where_is_independent_across_groups():
    v = _v([10, 20, 1, 2, 100, 200, 3, 4])
    g = pd.Series([1, 1, 1, 1, 2, 2, 2, 2], index=v.index)
    member = pd.Series([True, True, False, False, True, True, False, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=2)
    assert out.tolist() == pytest.approx([15.0, 15.0, 15.0, 15.0, 150.0, 150.0, 150.0, 150.0])


def test_group_mean_where_nulls_a_group_below_the_member_size_floor():
    v = _v([1, 2, 3, 10, 20])
    g = pd.Series([1] * 5, index=v.index)
    member = pd.Series([True, True, False, False, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=5)
    assert out.isna().all(), "2 members must not clear a floor of 5"


def test_group_mean_where_nulls_rows_with_no_group():
    v = _v([1, 2, 3, 4, 5, 6])
    g = pd.Series([1, 1, 1, 1, 1, np.nan], index=v.index)
    member = pd.Series([True, True, True, True, True, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=5)
    assert np.isnan(out.iloc[5])
    assert out.iloc[:5].tolist() == pytest.approx([3.0] * 5)


def test_group_mean_where_null_member_mask_treated_as_non_member():
    v = _v([1, 2, 3, 4, 5])
    g = pd.Series([1] * 5, index=v.index)
    member = pd.Series([True, True, True, True, True], index=v.index, dtype=object)
    member.iloc[-1] = np.nan
    out = group_mean_where(v, g, member, min_group=4)
    assert out.tolist() == pytest.approx([2.5] * 5)


def test_group_mean_where_a_non_member_null_value_can_still_be_assigned():
    v = _v([10, 20, 30, np.nan])
    g = pd.Series([1] * 4, index=v.index)
    member = pd.Series([True, True, True, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=3)
    assert out.tolist() == pytest.approx([20.0, 20.0, 20.0, 20.0])


def test_group_mean_where_preserves_the_input_index_and_length():
    v = _v([1, 2, 3, 4])
    g = pd.Series([1] * 4, index=v.index)
    member = pd.Series([True] * 4, index=v.index)
    out = group_mean_where(v, g, member, min_group=2)
    assert out.index.equals(v.index) and len(out) == len(v)


def test_group_mean_where_floor_counts_only_non_null_member_values():
    v = _v([1, 2, 3, 4, np.nan, 9])
    g = pd.Series([1] * 6, index=v.index)
    member = pd.Series([True, True, True, True, True, False], index=v.index)
    assert group_mean_where(v, g, member, min_group=5).isna().all(), \
        "a NaN-valued member must not count toward the floor"
    out = group_mean_where(v, g, member, min_group=4)
    assert out.tolist() == pytest.approx([2.5] * 6), "the NaN member still receives its group's mean"


def test_group_mean_where_a_group_with_no_members_is_nan():
    v = _v([10, 20, 1, 2])
    g = pd.Series([1, 1, 2, 2], index=v.index)
    member = pd.Series([True, True, False, False], index=v.index)
    out = group_mean_where(v, g, member, min_group=2)
    assert out.iloc[:2].tolist() == pytest.approx([15.0, 15.0])
    assert out.iloc[2:].isna().all()


def test_group_mean_where_no_members_at_all_is_all_nan():
    v = _v([1, 2, 3])
    g = pd.Series([1] * 3, index=v.index)
    member = pd.Series([False] * 3, index=v.index)
    assert group_mean_where(v, g, member, min_group=1).isna().all()


def test_group_mean_where_nullable_boolean_mask_with_na_is_non_member():
    v = _v([1, 2, 3, 4, 5])
    g = pd.Series([1] * 5, index=v.index)
    member = pd.Series([True, True, True, True, pd.NA], index=v.index, dtype="boolean")
    out = group_mean_where(v, g, member, min_group=4)
    assert out.tolist() == pytest.approx([2.5] * 5)


def test_group_mean_where_positional_inputs_align_or_raise():
    v = _v([10, 20, 30])
    out = group_mean_where(v, np.array([1, 1, 1]), np.array([True, True, False]), min_group=2)
    assert out.tolist() == pytest.approx([15.0] * 3)
    with pytest.raises(ValueError):
        group_mean_where(v, np.array([1, 1]), np.array([True, True, False]), min_group=2)
