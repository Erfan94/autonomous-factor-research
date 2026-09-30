import shutil
from pathlib import Path

import pytest
import yaml

from harness import provenance as PV


def test_stamps_are_twelve_hex():
    s = PV.all_stamps()
    for k in ("harness_sha", "config_sha", "composite_sha", "universe_sha"):
        assert len(s[k]) == 12 and int(s[k], 16) >= 0


def test_data_sha_is_nodata_until_a_snapshot_is_recorded():
    assert PV.data_sha({"status": "EMPTY", "tables": {}}) == "nodata"
    assert PV.data_sha({"tables": {}}) == "nodata"


def test_data_sha_depends_only_on_the_per_table_hashes():
    a = {"status": "FROZEN", "recorded_on": "x", "tables": {"SEP": {"sha256": "aa", "rows": 1}}}
    b = {"status": "FROZEN", "recorded_on": "y", "tables": {"SEP": {"sha256": "aa", "rows": 2}}}
    c = {"status": "FROZEN", "tables": {"SEP": {"sha256": "ab"}}}
    assert PV.data_sha(a) == PV.data_sha(b)
    assert PV.data_sha(a) != PV.data_sha(c)


def test_config_sha_moves_on_any_byte(tmp_path):
    p = tmp_path / "c.yaml"
    shutil.copy(PV.CONFIG_PATH, p)
    before = PV.config_sha(p)
    p.write_text(p.read_text() + "\n# a comment\n")
    assert PV.config_sha(p) != before


def test_universe_sha_ignores_non_universe_edits():
    cfg = PV.load_config()
    a = PV.universe_sha(cfg)
    cfg2 = dict(cfg); cfg2["acceptance_thresholds"] = {}
    assert PV.universe_sha(cfg2) == a


def test_composite_sha_covers_the_accepted_files_it_imports(tmp_path):
    comp = tmp_path / "composite.py"
    acc = tmp_path / "accepted"; acc.mkdir()
    (acc / "Foo.py").write_text("FACTOR = 1\n")
    comp.write_text("from factors.accepted.Foo import FACTOR as FOO\nCOMPOSITE_FACTORS=[FOO]\n")
    a = PV.composite_sha(comp, acc)
    (acc / "Foo.py").write_text("FACTOR = 2\n")
    assert PV.composite_sha(comp, acc) != a, "an accepted file's bytes must move the hash"


def test_composite_sha_refuses_a_missing_import(tmp_path):
    comp = tmp_path / "composite.py"
    (tmp_path / "accepted").mkdir()
    comp.write_text("from factors.accepted.Missing import FACTOR as M\n")
    with pytest.raises(FileNotFoundError):
        PV.composite_sha(comp, tmp_path / "accepted")


def test_harness_sha_covers_every_harness_module():
    for f in PV.HARNESS_FILES:
        assert (PV.HARNESS_DIR / f).exists(), f
    # the reverse: every module that can move a number is hashed; only the
    # package marker and the data step (stamped by DATA_SHA) are exempt
    exempt = {"__init__.py", "snapshot.py"}
    on_disk = {p.name for p in PV.HARNESS_DIR.glob("*.py")} - exempt
    assert on_disk == set(PV.HARNESS_FILES), sorted(on_disk ^ set(PV.HARNESS_FILES))
