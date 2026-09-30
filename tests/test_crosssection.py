import numpy as np
import pandas as pd
import pytest

from harness.crosssection import cs_trim, ols_residual


def _idx(n):
    return [f"id{i:03d}" for i in range(n)]


# ---- ols_residual -----------------------------------------------------------

def test_ols_residual_recovers_an_exact_linear_relation():
    rng = np.random.default_rng(0)
    idx = _idx(50)
    X = pd.DataFrame({"a": rng.normal(size=50), "b": rng.normal(size=50)}, index=idx)
    y = 1.5 + 2.0 * X["a"] - 3.0 * X["b"]
    r = ols_residual(y, X, min_obs=10)
    assert np.allclose(r.to_numpy(), 0.0, atol=1e-10)


def test_ols_residual_is_orthogonal_to_x_and_mean_zero_with_intercept():
    rng = np.random.default_rng(1)
    idx = _idx(200)
    X = pd.DataFrame({"a": rng.normal(size=200), "b": rng.normal(size=200)}, index=idx)
    y = pd.Series(0.3 * X["a"].to_numpy() + rng.normal(size=200), index=idx)
    r = ols_residual(y, X)
    assert abs(r.mean()) < 1e-10
    assert abs((r * X["a"]).sum()) < 1e-8
    assert abs((r * X["b"]).sum()) < 1e-8


def test_ols_residual_nan_rows_are_excluded_from_the_fit_and_nan_in_output():
    rng = np.random.default_rng(2)
    idx = _idx(40)
    X = pd.DataFrame({"a": rng.normal(size=40)}, index=idx)
    y = 2.0 * X["a"] + 1.0
    y_bad = y.copy()
    y_bad.iloc[3] = np.nan
    X_bad = X.copy()
    X_bad.iloc[7, 0] = np.nan
    y_bad.iloc[10] = 1e6                       # would wreck the fit if included...
    X_bad.iloc[10, 0] = np.nan                 # ...but its X is null, so it is not
    r = ols_residual(y_bad, X_bad, min_obs=5)
    assert np.isnan(r.iloc[3]) and np.isnan(r.iloc[7]) and np.isnan(r.iloc[10])
    assert np.allclose(r.drop(r.index[[3, 7, 10]]).to_numpy(), 0.0, atol=1e-10)


def test_ols_residual_min_obs_and_degrees_of_freedom_bite():
    idx = _idx(5)
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0]}, index=idx)
    y = pd.Series([1.0, 3.0, 2.0, 5.0, 4.0], index=idx)
    assert ols_residual(y, X, min_obs=6).isna().all()
    assert ols_residual(y, X, min_obs=3).notna().all()
    X2 = pd.DataFrame(np.arange(20.0).reshape(5, 4) ** 1.5, index=idx)
    assert ols_residual(y, X2, min_obs=1).isna().all(), "5 rows cannot fit 5 coefficients"


def test_ols_residual_fit_mask_scores_rows_outside_the_fit_from_mask_coefficients():
    idx = _idx(6)
    X = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0, 10.0, 20.0]}, index=idx)
    y = pd.Series([1.0, 3.0, 5.0, 7.0, 0.0, 0.0], index=idx)      # fit rows: y = 1 + 2a
    mask = pd.Series([True, True, True, True, False, False], index=idx)
    r = ols_residual(y, X, fit_mask=mask, min_obs=3)
    assert np.allclose(r.iloc[:4].to_numpy(), 0.0, atol=1e-10)
    assert r.iloc[4] == pytest.approx(0.0 - (1 + 2 * 10))
    assert r.iloc[5] == pytest.approx(0.0 - (1 + 2 * 20))


def test_ols_residual_without_intercept_and_with_dummies():
    idx = _idx(8)
    g = pd.Series(list("aabbccdd"), index=idx)
    D = pd.get_dummies(g, drop_first=True, dtype=float)
    y = pd.Series([1.0, 3.0, 10.0, 12.0, 5.0, 7.0, 0.0, 2.0], index=idx)
    r = ols_residual(y, D, min_obs=4)                               # group means removed
    assert r.tolist() == pytest.approx([-1, 1, -1, 1, -1, 1, -1, 1])
    X = pd.DataFrame({"a": [1.0, 2, 3, 4, 5, 6, 7, 8]}, index=idx)
    r0 = ols_residual(3.0 * X["a"], X, add_intercept=False, min_obs=4)
    assert np.allclose(r0.to_numpy(), 0.0, atol=1e-10)


def test_ols_residual_preserves_index_and_ignores_null_mask_entries():
    idx = _idx(10)
    X = pd.DataFrame({"a": np.arange(10.0)}, index=idx)
    y = 2.0 * X["a"]
    mask = pd.Series([True] * 9 + [np.nan], index=idx, dtype=object)
    r = ols_residual(y, X, fit_mask=mask, min_obs=3)
    assert list(r.index) == idx
    assert np.allclose(r.to_numpy(), 0.0, atol=1e-10)


# ---- cs_trim ----------------------------------------------------------------

def test_cs_trim_drops_both_tails_and_keeps_the_interior():
    idx = _idx(101)
    x = pd.Series(np.arange(101.0), index=idx)                      # percentiles 1 and 99 = 1 and 99
    t = cs_trim(x, 1, 99)
    assert np.isnan(t.iloc[0]) and np.isnan(t.iloc[100])
    assert t.iloc[1:100].tolist() == x.iloc[1:100].tolist()


def test_cs_trim_passes_nan_through_and_handles_all_null():
    x = pd.Series([np.nan, 1.0, 2.0, 3.0, np.nan], index=_idx(5))
    t = cs_trim(x, 0, 100)
    assert t.isna().tolist() == [True, False, False, False, True]
    allnan = pd.Series([np.nan] * 3, index=_idx(3))
    assert cs_trim(allnan).isna().all()


def test_cs_trim_uses_only_the_values_passed():
    a = pd.Series(np.arange(101.0), index=_idx(101))
    b = pd.Series(np.arange(101.0) * 1000, index=_idx(101))
    assert cs_trim(a).notna().sum() == cs_trim(b).notna().sum() == 99
