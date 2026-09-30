import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.provenance import ROOT, load_config  # noqa: E402
from tests.fixtures.synthetic_snapshot import build  # noqa: E402


@pytest.fixture(scope="session")
def synthetic(tmp_path_factory):
    root = tmp_path_factory.mktemp("snap")
    root, manifest, perma = build(root)
    return {"root": root, "manifest": manifest, "perma": perma}


@pytest.fixture(scope="session")
def cfg():
    """The real config with the window moved onto the fixture's years. Every
    other parameter is the project's — the tests exercise the real screens."""
    c = load_config()
    c["dates"]["eval_start"] = "1998-06-01"
    c["dates"]["eval_end"] = "2001-06-30"
    c["dates"]["out_of_sample_start"] = "2001-07-01"
    c["dates"]["out_of_sample_end"] = "2001-12-31"        # the fixture's last month (END)
    c["rebalance"]["min_months"] = 12
    c["universe"]["categories"] = ["Domestic Common Stock"]
    return c


@pytest.fixture(scope="session")
def runtime(synthetic):
    return {"data": {"root": str(synthetic["root"] / "sharadar"),
                     "manifest": str(synthetic["root"] / "SNAPSHOT_MANIFEST.yaml"),
                     "required_tables": ["SEP", "SF1", "DAILY", "TICKERS", "ACTIONS"],
                     "optional_tables": []},
            "cache": {"dir": str(synthetic["root"] / "cache"), "enabled": True},
            "results": {"dir": str(synthetic["root"] / "results"), "tee_stdout": False}}


@pytest.fixture(scope="session")
def snap(synthetic, runtime):
    from harness.data_layer import Snapshot
    return Snapshot(synthetic["root"] / "sharadar", synthetic["manifest"], verify_hashes=True)


@pytest.fixture(scope="session")
def panel(snap, cfg):
    from harness.data_layer import build_monthly_panel
    return build_monthly_panel(snap, cfg, log=lambda *a, **k: None)


@pytest.fixture(scope="session")
def pidx(panel, snap, cfg):
    from harness.data_layer import PanelIndex
    return PanelIndex(panel, snap, cfg)
