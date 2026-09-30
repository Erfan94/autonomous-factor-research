#!/usr/bin/env python3
"""
Record maintenance — keeps the files the loop reads every turn SMALL.

    python3 scripts/records.py index      # rebuild research/registry_index.yaml from research/registry/*.yaml
    python3 scripts/records.py fieldmap   # rebuild osap_source/field_map_index.yaml from field_map.yaml
    python3 scripts/records.py state      # print the current session state
    python3 scripts/records.py frontier   # check, printing the OSAP open frontier in full
    python3 scripts/records.py check      # drift: index vs rows, events schema, state size, phase gate, stranded runs

The full registry rows live one per file in research/registry/; the index is
derived and is what CLAUDE.md step 2 and factor-evaluator read. Rebuilding it
is idempotent.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "research" / "registry"
INDEX = ROOT / "research" / "registry_index.yaml"
FMAP = ROOT / "osap_source" / "field_map.yaml"
FMAP_INDEX = ROOT / "osap_source" / "field_map_index.yaml"
EVENTS = ROOT / "research" / "events.jsonl"
STAMP_KEYS = ("harness_sha", "config_sha", "composite_sha", "data_sha")
STATE = ROOT / "research" / "session_state.yaml"
RESULTS = ROOT / "research" / "results"
LIVE_CHECK = ROOT / "research" / "live_check.yaml"
FULL_FRONTIER = False

KNOWN_EVENTS = {
    "project_initialized", "snapshot_recorded", "factor_suggested", "factor_fetched",
    "factor_infeasible", "factor_dropped", "factor_deferred", "factor_translated",
    "fields_verified", "batch_declared", "batch_amended", "preflight_failed", "preflight_remeasured", "run_started",
    "run_completed", "run_failed", "provenance_verified", "provenance_mismatch",
    "validation_warning", "factor_evaluated", "batch_closed", "registry_rows_written",
    "spec_written", "inventory_classified", "family_assigned", "stage2_order_declared",
    "phase_completed",
    "composite_updated", "construction_reported", "config_changed", "harness_changed",
    "harness_defect_found", "finding_confirmed", "finding_corrected", "process_finding",
    "open_question_updated", "decision_reversed", "repository_initialized",
    "repository_pushed", "repository_committed", "alpha_review", "error", "flip_hypothesis_qualified",
    "frontier_classified",
    "preflight_passed",
}


def _g(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def build_index():
    rows = []
    for p in sorted(REG.glob("*.yaml")):
        r = yaml.safe_load(p.read_text()) or {}
        s1, s2 = r.get("stage1") or {}, r.get("stage2") or {}
        rows.append({
            "name": r.get("name", p.stem), "status": r.get("status"), "batch": r.get("batch"),
            "ic": _g(s1, "ic_mean"), "ic_t": _g(s1, "ic_tstat_nw"), "sharpe": _g(s1, "ls_sharpe"),
            "ret": _g(s1, "ls_ann_return_pct"), "raw_ret": _g(s1, "ls_raw_ann_return_pct"),
            "cov": _g(s1, "coverage_pct"),
            "resid_t": _g(s2, "resid_ic_tstat_nw"), "span_t": _g(s2, "spanning_alpha_tstat_nw"),
            "dic_t": _g(s2, "paired_delta_ic_tstat"), "dls_t": _g(s2, "paired_delta_ls_tstat"),
            "d_sharpe": _g(s2, "delta_ls_sharpe"),
            "beta": _g(s1, "ls_beta_fullwindow"), "sh_exreg": _g(s1, "ls_sharpe_ex_top_years"),
            "family": r.get("family"),
            "decided_by": r.get("decided_by"), "run": r.get("run"),
        })
    counts = Counter(r["status"] for r in rows)
    acc = {"n_candidates_suggested": sum(1 for r in rows if r["status"] not in ("baseline",)),
           "n_stage1_tested": sum(1 for r in rows if r["ic"] is not None),
           "n_stage1_passed": sum(1 for r in rows if r["status"] in ("accepted", "rejected_stage2", "stage2_pending")
                                  or (r["status"] == "rejected" and r["resid_t"] is not None)),
           "n_stage2_tested": sum(1 for r in rows if r["resid_t"] is not None),
           "n_accepted": counts.get("accepted", 0),
           "n_inconclusive": counts.get("inconclusive", 0),
           "by_status": dict(sorted(counts.items()))}
    lines = ["# DERIVED — rebuilt by `python3 scripts/records.py index` from research/registry/*.yaml.",
             "# One line per factor; the full row is research/registry/<name>.yaml. Never edit by hand.",
             "search_accounting:"]
    for k, v in acc.items():
        lines.append(f"  {k}: {json.dumps(v) if isinstance(v, dict) else v}")
    lines.append("factors:")

    def f(v, nd=4):
        return "null" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))
    for r in rows:
        lines.append(f"  - {{name: {r['name']}, status: {r['status']}, batch: {r['batch']}, "
                     f"ic: {f(r['ic'])}, ic_t: {f(r['ic_t'], 2)}, sharpe: {f(r['sharpe'], 3)}, "
                     f"ret: {f(r['ret'], 2)}, cov: {f(r['cov'], 1)}, resid_t: {f(r['resid_t'], 2)}, "
                     f"dic_t: {f(r['dic_t'], 2)}, dls_t: {f(r['dls_t'], 2)}, span_t: {f(r['span_t'], 2)}, d_sharpe: {f(r['d_sharpe'], 3)}, "
                     f"beta: {f(r['beta'], 2)}, sh_exreg: {f(r['sh_exreg'], 3)}, "
                     f"family: {json.dumps(r['family'])}, decided_by: {json.dumps(r['decided_by'])}, run: {json.dumps(r['run'])}}}")
    INDEX.write_text("\n".join(lines) + "\n")
    print(f"index: {len(rows)} rows, {INDEX.stat().st_size} bytes; {dict(counts)}")


def build_fieldmap_index():
    """One line per Compustat/CRSP input: the Sharadar field, status, note."""
    fm = yaml.safe_load(FMAP.read_text()) or {}
    out = ["# DERIVED — rebuilt by `python3 scripts/records.py fieldmap` from field_map.yaml.",
           "# One line per input: target field, status, note. Open field_map.yaml only for a field's detail.",
           "fields:"]
    n = 0
    for section in ("compustat_to_sf1", "crsp_to_sharadar"):
        for key, node in (fm.get(section) or {}).items():
            if not isinstance(node, dict):
                continue
            tgt = node.get("sf1") or node.get("sharadar") or node.get("maps_to") or ""
            note = str(node.get("note") or node.get("deviation") or "").replace("\n", " ").strip()[:110]
            out.append(f"  - {{key: {json.dumps(section.split('_')[0] + '.' + str(key))}, "
                       f"sharadar: {json.dumps(str(tgt))}, status: {json.dumps(str(node.get('status')))}, "
                       f"verified_on: {json.dumps(str(node.get('verified_on', '')))}, note: {json.dumps(note)}}}")
            n += 1
    traps = fm.get("known_traps") or []
    out.append(f"known_traps: {len(traps)}   # read field_map.yaml `known_traps` before touching prices, shares, marketcap, dimensions")
    FMAP_INDEX.write_text("\n".join(out) + "\n")
    print(f"field map index: {n} entries, {FMAP_INDEX.stat().st_size} bytes")


def show_state():
    print(STATE.read_text())


def phase_gate(rows):
    """The search runs in phases and Stage 2 may not start early. DRIFT when a
    Stage 2 run exists while (a) a constructible predictor (a file under
    factors/candidates/) has no Stage 1 row, or (b) a Stage 1 passer has no
    family. Stage 2 order is descending Stage 1 NW t over ALL passers, so a
    ladder declared before the inventory is fully screened and categorised
    would be ordered on an incomplete list."""
    if not EVENTS.exists():
        return True
    stage2_started = False
    for line in EVENTS.read_text().splitlines():
        if '"run_started"' not in line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("event") == "run_started" and str(e.get("stage")) == "2":
            stage2_started = True
            break
    if not stage2_started:
        return True
    ok = True
    pool = {p.stem for p in (ROOT / "factors" / "candidates").glob("*.py") if not p.stem.startswith("_")}
    untested = sorted(pool - set(rows))
    if untested:
        ok = False
        print(f"phase gate: Stage 2 has started but {len(untested)} constructible predictors have no "
              f"Stage 1 row: {', '.join(untested[:8])}{' ...' if len(untested) > 8 else ''}")
    unassigned = []
    for p in sorted(REG.glob("*.yaml")):
        r = yaml.safe_load(p.read_text()) or {}
        if str(r.get("stage1_decision", "")).upper() == "PASS" and not r.get("family"):
            unassigned.append(r.get("name", p.stem))
    if unassigned:
        ok = False
        print(f"phase gate: Stage 2 has started but {len(unassigned)} Stage 1 passers have no family: "
              f"{', '.join(unassigned[:8])}{' ...' if len(unassigned) > 8 else ''}")
    return ok


def osap_frontier(rows):
    """Reconcile OSAP's predictor list against everything this repo accounts for.

    The frontier is SignalDoc's Predictor rows, never the files on disk: a
    file-based frontier hides predictors that were never looked at, and the
    baseline legs sit in the index under project names (Size, Value,
    Profitability, Investment, Momentum) while OSAP calls them Size, BM,
    OperProf, AssetGrowth, Mom12m. Accounted-for means: a registry row, a
    leg's osap_acronym, a candidate/accepted file, or a logged exclusion in
    osap_frontier.yaml. The inventory phase (CLAUDE.md, Phase A) ends when
    UNACCOUNTED is 0.
    """
    doc = ROOT / "osap_source" / "cache" / "b4e911e6" / "SignalDoc.csv"
    if not doc.exists():
        return True
    with doc.open(newline="", encoding="utf-8-sig") as fh:
        rdr = list(csv.DictReader(fh))
    if not rdr:
        return True
    cat = next((c for c in rdr[0] if "Cat.Signal" in c), None)
    acr = {(r.get("Acronym") or "").strip() for r in rdr
           if cat and (r.get(cat) or "").strip() == "Predictor"}
    acr.discard("")
    legs = set(re.findall(r'osap_acronym="(\w+)"', (ROOT / "factors" / "composite.py").read_text()))
    files = {p.stem for p in (ROOT / "factors" / "candidates").glob("*.py")} | \
            {p.stem for p in (ROOT / "factors" / "accepted").glob("*.py")}
    for _d in ("candidates", "accepted"):          # a file translated under a new name
        for _p in (ROOT / "factors" / _d).glob("*.py"):   # still accounts for its acronym
            files |= set(re.findall(r'osap_acronym="(\w+)"', _p.read_text()))
    files = {f for f in files if not f.startswith("_")}
    excl = {}
    fpath = ROOT / "osap_source" / "osap_frontier.yaml"
    if fpath.exists():
        excl = (yaml.safe_load(fpath.read_text()) or {}).get("excluded", {}) or {}
    known = set(rows) | legs | files | set(excl)
    open_names = sorted(acr - known)
    print(f"OSAP predictors: {len(acr)}; accounted {len(acr & known)} "
          f"(rows {len(acr & set(rows))}, legs {len(acr & legs)}, files {len(acr & files)}, "
          f"logged-excluded {len(acr & set(excl))}); UNACCOUNTED {len(open_names)}")
    if open_names:
        n = len(open_names) if FULL_FRONTIER else 12
        print("  open frontier: " + ", ".join(open_names[:n]) +
              (f" ... (+{len(open_names) - n})" if len(open_names) > n else ""))
        print("  -> screen them, or log each with a reason in osap_source/osap_frontier.yaml")
    ok_src = phase_gate(rows)
    stale = sorted(set(excl) - acr)
    if stale:
        print(f"  osap_frontier.yaml names that are not OSAP predictors: {stale}")
        return False
    return ok_src


def unevaluated_runs():
    """A completed run whose stamps no longer match the repo can never be
    verified: `factor-evaluator` refuses a result whose provenance has moved,
    and rightly so. So a stamp must not move while any completed run is
    unevaluated — ANY of the four, not just HARNESS_SHA. This is the
    check that catches it. Stamps come from each run's own
    `.meta.json`, the artifact the evaluator reads, not from an event's
    shape: `run_completed` rows carry stamps from the runner."""
    # A run counts as read once ANY record other than the run_* events names it:
    # the evaluator's provenance_verified / factor_evaluated / registry_rows_written,
    # a construction_reported, or the nested seqs of a composite_updated. Early rows
    # carry a combined seq ("001,002"), so split on commas.
    verified = set()
    if EVENTS.exists():
        for line in EVENTS.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("event") in ("run_started", "run_completed", "run_failed"):
                continue
            seq = e.get("seq")
            raw = list(seq.values()) if isinstance(seq, dict) else [seq]
            for r in raw:
                verified |= {t.strip() for t in str(r or "").split(",") if t.strip()}
    sys.path.insert(0, str(ROOT / "harness"))
    import provenance

    now = provenance.all_stamps()
    ok = True
    for meta in sorted(RESULTS.glob("*.meta.json")):
        d = json.loads(meta.read_text())
        seq = f"{int(d['seq']):03d}"
        if seq in verified:
            continue
        stamps = d.get("stamps") or {}
        moved = [k for k in STAMP_KEYS if stamps.get(k) and stamps[k] != now.get(k)]
        if moved:
            ok = False
            detail = "; ".join(f"{k} {stamps[k]} != repo {now[k]}" for k in moved)
            print(f"  STRANDED: run {seq} is unevaluated and its stamps have moved — {detail}")
            print("            re-run it under the current stamps; it cannot be evaluated as it stands")
        else:
            print(f"  unevaluated run {seq} — evaluate it before moving any stamp")
    return ok


def live_check_fresh(max_age_days=14):
    """The snapshot must be a materialisation of the API, not a cache nobody
    re-reads. `harness/snapshot.py live` proves that against the vendor and
    writes research/live_check.yaml; this is the offline half, run every turn,
    which refuses a proof that is missing, was measured against a DIFFERENT
    DATA_SHA, or has gone stale. Without it "we check the API" degrades into
    "we checked the API once", which is what let four tables sit unmapped for
    a whole search."""
    import datetime

    sys.path.insert(0, str(ROOT / "harness"))
    import provenance

    now_sha = provenance.data_sha()
    if not LIVE_CHECK.exists():
        print("  no live API verification on record — run `python3 harness/snapshot.py live`")
        return False
    rec = yaml.safe_load(LIVE_CHECK.read_text()) or {}
    if rec.get("data_sha") != now_sha:
        print(f"  live API verification is against DATA_SHA {rec.get('data_sha')}, repo is {now_sha}"
              " — re-run `python3 harness/snapshot.py live`")
        return False
    if not rec.get("column_complete", False):
        print(f"  last live API verification FAILED: {rec.get('problems')}")
        return False
    try:
        age = (datetime.datetime.now(datetime.timezone.utc)
               - datetime.datetime.strptime(rec["checked_at"], "%Y-%m-%dT%H:%M:%SZ")
               .replace(tzinfo=datetime.timezone.utc)).days
    except Exception:
        print("  live API verification has no readable timestamp — re-run it")
        return False
    if age > max_age_days:
        print(f"  live API verification is {age} days old (limit {max_age_days}) — re-run it")
        return False
    absent = rec.get("mapped_but_absent") or []
    tail = f"; mapped but not held: {', '.join(absent)}" if absent else ""
    print(f"  live API: {rec['tables_checked']} tables column-complete, checked {age}d ago"
          f" against this DATA_SHA{tail}")
    return True


def check():
    ok = True
    names = {p.stem for p in REG.glob("*.yaml")}
    idx = yaml.safe_load(INDEX.read_text()) if INDEX.exists() else {}
    in_idx = {r["name"] for r in ((idx or {}).get("factors") or [])}
    if names != in_idx:
        ok = False
        print(f"index drift: rows {sorted(names ^ in_idx)} — run `records.py index`")
    if EVENTS.exists():
        unknown = Counter()
        for line in EVENTS.read_text().splitlines():
            if line.strip():
                e = json.loads(line)
                if e.get("event") not in KNOWN_EVENTS:
                    unknown[e.get("event")] += 1
        if unknown:
            ok = False
            print(f"unknown event types: {dict(unknown)} — add to research/RECORDS.md and KNOWN_EVENTS")
    n_lines = len(STATE.read_text().splitlines())
    if n_lines > 40:
        ok = False
        print(f"session_state.yaml is {n_lines} lines; keep the current state only (≤ 40)")
    pool = {p.stem for p in (ROOT / "factors" / "candidates").glob("*.py") if not p.stem.startswith("_")}
    print(f"candidate pool on disk: {len(pool)}; registry rows: {len(names)}; untested pool: {len(pool - names)}")
    ok = osap_frontier(names) and ok
    ok = unevaluated_runs() and ok
    ok = live_check_fresh() and ok
    print("OK" if ok else "DRIFT")
    sys.exit(0 if ok else 1)


def main():
    global FULL_FRONTIER
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "frontier":
        FULL_FRONTIER, cmd = True, "check"
    {"index": build_index, "fieldmap": build_fieldmap_index, "state": show_state, "check": check}[cmd]()


if __name__ == "__main__":
    main()
