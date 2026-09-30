from factors import composite as C
from harness.factor_def import FactorDef


def test_composite_starts_with_the_five_ff_plus_momentum_legs():
    names = [f.name for f in C.active_factors()]
    assert names[:5] == ["Size", "Value", "Profitability", "Investment", "Momentum"]
    assert C.COMPOSITE_VERSION.startswith("v")


def test_every_leg_validates():
    for f in C.COMPOSITE_FACTORS:
        assert f.validate() == [], f.name


SEEDS = ["size", "value", "profitability", "investment", "momentum"]


def test_every_leg_declares_a_family_and_the_seeds_open_the_five_seed_families():
    fams = C.families()
    assert all(f.family for f in C.COMPOSITE_FACTORS)
    assert list(fams)[:5] == SEEDS
    assert [f.family for f in C.COMPOSITE_FACTORS[:5]] == SEEDS
    assert all(len(v) >= 1 for v in fams.values())
    assert len(fams) <= 9                                   # config search.families_max


def test_weights_are_the_family_blend_equal_across_families():
    w = C.weights()
    fams = C.families()
    assert abs(sum(w.values()) - 1.0) < 1e-12
    for names in fams.values():                             # 1/F per family, equal within
        assert abs(sum(w[n] for n in names) - 1 / len(fams)) < 1e-12
        assert len(set(round(w[n], 12) for n in names)) == 1


def test_a_candidate_joining_an_existing_family_dilutes_only_that_family():
    cand = FactorDef(name="X", col="f_x", compute=lambda c: None, ascending=True, weight=1.0,
                     family="value")
    w = C.weights_with(cand)
    fams = C.families()
    n_fam = len(fams)
    per_leg = 1 / (n_fam * (len(fams["value"]) + 1))        # value may already hold more than one leg
    assert abs(w["X"] - per_leg) < 1e-12 and all(abs(w[n] - per_leg) < 1e-12 for n in fams["value"])
    assert abs(w["Size"] - 1 / n_fam) < 1e-12 and abs(sum(w.values()) - 1.0) < 1e-12


def test_a_candidate_opening_a_new_family_gets_a_full_family_weight():
    cand = FactorDef(name="X", col="f_x", compute=lambda c: None, ascending=True, weight=1.0,
                     family="brand_new_family")
    w = C.weights_with(cand)
    fams = C.families()
    n_fam = len(fams) + 1
    assert abs(w["X"] - 1 / n_fam) < 1e-12
    for names in fams.values():
        assert abs(sum(w[n] for n in names) - 1 / n_fam) < 1e-12
    assert abs(sum(w.values()) - 1.0) < 1e-12


def test_a_candidate_without_a_family_is_refused_at_stage2_weighting():
    import pytest
    cand = FactorDef(name="X", col="f_x", compute=lambda c: None, ascending=True, weight=1.0)
    with pytest.raises(ValueError, match="family"):
        C.weights_with(cand)


def test_a_family_must_be_a_lower_case_slug():
    bad = FactorDef(name="B", col="f_b", compute=lambda c: None, ascending=True, weight=1.0,
                    family="Value Family")
    assert any("family" in p for p in bad.validate())


def test_a_leg_already_in_the_composite_is_refused():
    import pytest
    with pytest.raises(ValueError):
        C.weights_with(C.SIZE)


def test_momentum_declares_its_history_gate():
    assert C.MOMENTUM.history_months == 12


def test_a_price_factor_without_a_gate_is_rejected_by_validate():
    f = FactorDef(name="Bad", col="f_bad", compute=lambda c: None, ascending=True, weight=1.0,
                  inputs=("SEP.closeadj",))
    assert any("history_months" in p for p in f.validate())
    ok = FactorDef(name="Ok", col="f_ok", compute=lambda c: None, ascending=True, weight=1.0,
                   inputs=("SEP.closeadj",), no_history_gate_because="uses only the signal-date price")
    assert ok.validate() == []


def test_preflight_orientation_check_catches_a_flipped_sign():
    """A factor whose `ascending` contradicts SignalDoc's Sign is a hard fail
    unless it is a declared '*Flip' second hypothesis."""
    import dataclasses
    from harness.preflight import check_orientation
    from harness.provenance import load_config
    from factors.composite import COMPOSITE_FACTORS
    cfg = load_config()
    leg = COMPOSITE_FACTORS[0]
    hard, _ = check_orientation([leg], cfg)
    assert hard == []
    flipped = dataclasses.replace(leg, ascending=not leg.ascending)
    hard, _ = check_orientation([flipped], cfg)
    assert len(hard) == 1 and "contradicts SignalDoc" in hard[0]
    declared = dataclasses.replace(flipped, name=leg.name + "Flip")
    hard, _ = check_orientation([declared], cfg)
    assert hard == []
