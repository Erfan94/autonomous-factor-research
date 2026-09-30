"""
The four stamps. Every result block carries them; factor-evaluator refuses a
result whose stamps do not match the repo.

  HARNESS_SHA    harness/analytics.py + crosssection.py + data_layer.py +
                 factor_def.py + industry.py + portfolio.py + preflight.py +
                 provenance.py + run_test.py + construction_layer.py — the code that turns a
                 snapshot and a factor into a number. Every harness module
                 except __init__.py and snapshot.py (the data step, whose
                 output DATA_SHA stamps) is here; a test pins it.
  CONFIG_SHA     config/test_config.yaml — every parameter that can move a
                 number. config/runtime.yaml is deliberately excluded.
  COMPOSITE_SHA  factors/composite.py + every file in factors/accepted/ that
                 the composite imports, in a fixed order. The BQuant project
                 pasted accepted code into composite.py verbatim so one file's
                 hash covered it; hashing the imported files achieves the same
                 without the duplication.
  DATA_SHA       data/SNAPSHOT_MANIFEST.yaml's per-table sha256 values. A
                 refreshed snapshot moves it. This is the stamp the BQuant
                 project could not have: its vendor data moved under it by
                 ~0.03% between fetches, and nothing recorded which fetch a
                 row was measured on.

  UNIVERSE_SHA   the `universe` block of the config alone. A cache key, not a
                 comparability stamp, so a factor-only config edit does not
                 invalidate the cached universe panel.

Twelve hex characters each, like the BQuant project, so the two registries
read alike.

    python3 harness/provenance.py          # print all four
"""

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
HARNESS_DIR = ROOT / "harness"
CONFIG_PATH = ROOT / "config" / "test_config.yaml"
RUNTIME_PATH = ROOT / "config" / "runtime.yaml"
COMPOSITE_PATH = ROOT / "factors" / "composite.py"
ACCEPTED_DIR = ROOT / "factors" / "accepted"
CANDIDATES_DIR = ROOT / "factors" / "candidates"
MANIFEST_PATH = ROOT / "data" / "SNAPSHOT_MANIFEST.yaml"

HARNESS_FILES = ["analytics.py", "crosssection.py", "data_layer.py", "factor_def.py",
                 "industry.py", "portfolio.py", "preflight.py", "provenance.py", "run_test.py",
                 "construction_layer.py"]


def _sha(*texts):
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8") if isinstance(t, str) else t)
    return h.hexdigest()[:12]


def _read(path):
    return Path(path).read_text(encoding="utf-8")


def load_config(path=CONFIG_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def load_runtime(path=RUNTIME_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def harness_sha(harness_dir=HARNESS_DIR):
    return _sha(*[_read(Path(harness_dir) / f) for f in HARNESS_FILES])


def config_sha(path=CONFIG_PATH):
    return _sha(_read(path))


def universe_sha(cfg=None):
    cfg = cfg or load_config()
    return _sha(yaml.safe_dump(cfg["universe"], sort_keys=True))


def accepted_files(composite_path=COMPOSITE_PATH, accepted_dir=ACCEPTED_DIR):
    """The accepted factor files the composite imports, in source order.

    Read off the composite's own `from factors.accepted.<Name> import` lines,
    so a file sitting in accepted/ that the composite does NOT import is not
    hashed as if it were live — and a file the composite imports but which is
    missing fails here rather than at run time.
    """
    names = []
    for line in _read(composite_path).splitlines():
        line = line.strip()
        if line.startswith("from factors.accepted.") and " import " in line:
            mod = line.split()[1].rsplit(".", 1)[-1]
            names.append(mod)
    paths = []
    for n in names:
        p = Path(accepted_dir) / f"{n}.py"
        if not p.exists():
            raise FileNotFoundError(f"composite.py imports factors.accepted.{n} "
                                    f"but {p} does not exist")
        paths.append(p)
    return paths


def composite_sha(composite_path=COMPOSITE_PATH, accepted_dir=ACCEPTED_DIR):
    parts = [_read(composite_path)]
    for p in accepted_files(composite_path, accepted_dir):
        parts.append(f"\n# ---- {p.name} ----\n")
        parts.append(_read(p))
    return _sha(*parts)


def load_manifest(path=MANIFEST_PATH):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def data_sha(manifest=None, path=MANIFEST_PATH):
    """Hash of the per-table sha256 values — NOT of the whole file, so editing
    a comment in the manifest cannot move it, and two manifests describing the
    same bytes agree. Returns "nodata" when no snapshot is recorded, which
    run_test.py refuses to run on."""
    m = manifest if manifest is not None else load_manifest(path)
    tables = m.get("tables") or {}
    if not tables or m.get("status") == "EMPTY":
        return "nodata"
    items = sorted((t, str(v.get("sha256", ""))) for t, v in tables.items())
    return _sha(*[f"{t}:{s}\n" for t, s in items])


def all_stamps():
    cfg = load_config()
    return {
        "harness_sha": harness_sha(),
        "config_sha": config_sha(),
        "composite_sha": composite_sha(),
        "data_sha": data_sha(),
        "universe_sha": universe_sha(cfg),
    }


if __name__ == "__main__":
    for k, v in all_stamps().items():
        print(f"{k:<14} {v}")
    sys.exit(0)
