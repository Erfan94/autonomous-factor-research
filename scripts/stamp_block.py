#!/usr/bin/env python3
"""
Print the stamp block a commit message must carry, with moved/unmoved marks
derived from the previous commit's message.

    python3 scripts/stamp_block.py            # against HEAD
    python3 scripts/stamp_block.py --check    # exit 1 if the tree's stamps are
                                              # not what HEAD's message claims

The four stamps are recomputed from the working tree, never copied from a
message. "unmoved" is the fact a reader most often needs and the one a diff
cannot show cheaply, so every commit carries all four.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness.provenance import all_stamps  # noqa: E402

NAMES = [("HARNESS_SHA", "harness_sha"), ("CONFIG_SHA", "config_sha"),
         ("COMPOSITE_SHA", "composite_sha"), ("DATA_SHA", "data_sha")]
LINE = re.compile(r"^(HARNESS_SHA|CONFIG_SHA|COMPOSITE_SHA|DATA_SHA)\s+(\S+)")


def stamps_in(message):
    out = {}
    for line in message.splitlines():
        m = LINE.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def head_message():
    try:
        return subprocess.run(["git", "log", "-1", "--format=%B"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return ""


def pytest_count():
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"],
                       cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) passed", r.stdout)
    return (m.group(1) if m else "?"), r.returncode == 0


def main():
    check = "--check" in sys.argv
    now = all_stamps()
    prev = stamps_in(head_message())
    if check:
        bad = [k for k, key in NAMES if prev.get(k) not in (None, now[key])]
        if bad:
            print("HEAD's message claims stamps the tree does not have: " + ", ".join(bad))
            sys.exit(1)
        print("stamps match HEAD's message")
        return
    n, ok = pytest_count()
    for label, key in NAMES:
        old = prev.get(label)
        mark = "unmoved" if old == now[key] else (f"moved from {old}" if old else "first commit")
        print(f"{label:<13} {now[key]}  ({mark})")
    print(f"{'pytest':<13} {n} passed" + ("" if ok else "  <-- FAILING, do not commit"))
    print(f"{'holdout':<13} {holdout_state()}")


def holdout_state():
    """`unspent`, or `SPENT <date>` from the manifest's top-level `holdout`
    block (the record the spend writes: RECORDS.md). The predecessor read a
    key nobody wrote and printed `unspent` after its spend."""
    try:
        import yaml
        m = yaml.safe_load(open(ROOT / "MODEL_MANIFEST.yaml")) or {}
    except Exception:
        return "unspent"
    h = m.get("holdout")
    if isinstance(h, dict):
        if h.get("spent_on") or h.get("status", "").lower() == "spent":
            return f"SPENT {h.get('spent_on', '')}".strip()
        return "unspent"
    if isinstance(h, str) and h.lower().startswith("spent"):
        return h
    return "unspent"


if __name__ == "__main__":
    main()
