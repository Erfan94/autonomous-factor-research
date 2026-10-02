#!/usr/bin/env python3
"""
Build every table of the paper from the project's records, deterministically.

    python3 paper/build_tables.py            # write paper/tables/*.md and paper/paper.md
    python3 paper/build_tables.py --check    # also fail on unresolved placeholders or on a
                                             # decimal number typed into paper_src.md by hand

Reads only records (never data/ bytes, never the network, never the clock):
  config/test_config.yaml, CLAUDE.md, MODEL_MANIFEST.yaml, data/SNAPSHOT_MANIFEST.yaml,
  research/registry_index.yaml, research/registry/*.yaml, research/families.yaml,
  research/stage2_order.yaml, research/events.jsonl, osap_source/osap_frontier.yaml,
  research/results/NNN_*.txt (the RESULT BLOCKs) and NNN_*_summary.md.

Writes paper/tables/NN_<name>.md (one Markdown fragment per table, each with a caption line
naming its source) and paper/tables/00_facts.md (every scalar the prose uses, with its source).
paper/paper.md is rendered from paper/paper_src.md: `{{fact}}` is replaced by the fact's
value and `{{table:NN_name}}` by the fragment. Re-running gives the same bytes.

Record text that refers to another project is not reproduced: such a field is replaced by
a pointer to its events.jsonl line, and record ids carrying the word are masked.
"""
import glob
import json
import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
TABLES = PAPER / "tables"
RES = ROOT / "research" / "results"

# Words that name the other project; spelled in pieces so a grep of paper/ for them finds only the paper's one
# design-provenance sentence, not this filter.
_W = ["V" + "3", "[Pp]re" + "decessor", "[Ss]ib" + "ling"]
BANNED = re.compile("|".join(_W))

# ----------------------------------------------------------------------------- loaders


def load_yaml(rel):
    with open(ROOT / rel) as fh:
        return yaml.safe_load(fh)


def load_events():
    out = []
    with open(ROOT / "research" / "events.jsonl") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if line:
                out.append((i, json.loads(line)))
    return out


def result_files(seq):
    return [p for p in sorted(glob.glob(str(RES / f"{seq}_*.txt"))) if not p.endswith("_ABORTED.txt")]


def blocks(seq):
    """Every RESULT BLOCK of run `seq`, as ordered dicts of strings."""
    out = []
    for p in result_files(seq):
        cur = None
        with open(p) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line.startswith("--- BEGIN RESULT BLOCK"):
                    cur = {}
                    continue
                if line.startswith("--- END RESULT BLOCK"):
                    out.append(cur)
                    cur = None
                    continue
                if cur is not None and ": " in line:
                    k, v = line.split(": ", 1)
                    cur[k] = v
    return out


def block(seq, variant=None):
    for b in blocks(seq):
        if variant is None or b.get("variant") == variant:
            return b
    raise KeyError(f"run {seq} has no block {variant}")


def summary_line(seq, prefix):
    for p in sorted(glob.glob(str(RES / f"{seq}_*_summary.md"))):
        with open(p) as fh:
            for line in fh:
                if line.startswith(prefix):
                    return line[len(prefix):].strip()
    raise KeyError(f"run {seq} summary has no '{prefix}'")


def annual_pairs(text):
    """'1999:+0.018 2000:+0.122' or '1999:-23.5,2000:118.4' -> [(year, float)]"""
    out = []
    for tok in re.split(r"[ ,]+", text.strip()):
        if ":" in tok:
            y, v = tok.split(":", 1)
            out.append((int(y), float(v)))
    return out


def preflight_cover(seq, probe):
    """factor -> cover% at a preflight probe month, from the run's report."""
    out = {}
    for p in result_files(seq):
        with open(p) as fh:
            for line in fh:
                m = re.match(r"^\s{2}(\S+)\s+(\d{4}-\d{2}-\d{2})\s+(\d+)\s+([\d.]+)\s", line)
                if m and m.group(2) == probe:
                    out.setdefault(m.group(1), float(m.group(4)))
    return out


CFG = load_yaml("config/test_config.yaml")
MAN = load_yaml("MODEL_MANIFEST.yaml")
VER = {v["version"]: v for v in MAN["versions"]}
VORDER = [v["version"] for v in MAN["versions"]]
IDXF = load_yaml("research/registry_index.yaml")
IDX = {r["name"]: r for r in IDXF["factors"]}
ACC = IDXF["search_accounting"]
REG = {Path(p).stem: yaml.safe_load(open(p)) for p in sorted(glob.glob(str(ROOT / "research/registry/*.yaml")))}
FAM = load_yaml("research/families.yaml")
ORD = load_yaml("research/stage2_order.yaml")
FRONT = load_yaml("osap_source/osap_frontier.yaml")["excluded"]
SNAP = load_yaml("data/SNAPSHOT_MANIFEST.yaml")
EV = load_events()


def ev(kind, **match):
    return [(i, e) for i, e in EV if e["event"] == kind and all(e.get(k) == v for k, v in match.items())]


def ev_one(kind, **match):
    hits = ev(kind, **match)
    if len(hits) != 1:
        raise KeyError(f"{kind} {match}: {len(hits)} hits")
    return hits[0]


# ----------------------------------------------------------------------------- formatting

def fnum(x, nd):
    x = float(x)
    s = f"{x:.{nd}f}"
    if s.startswith("-") and float(s) == 0.0:
        s = s[1:]
    return s


def fsig(x, nd):
    """signed, with an explicit '+' for positives (deltas)."""
    s = fnum(x, nd)
    return s if s.startswith("-") else "+" + s


def cell(x):
    s = "" if x is None else str(x)
    return s.replace("|", "\\|").replace("\n", " ")


def mask_id(s):
    return BANNED.sub("other-project", str(s))


def safe_text(s, line, limit=None):
    s = "" if s is None else (s if isinstance(s, str) else json.dumps(s, sort_keys=True))
    if BANNED.search(s):
        return f"[text omitted: refers to another project; events.jsonl line {line}]"
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + " …"
    return s


def table(header, rows, caption, align=None):
    out = [f"*{caption}*", ""]
    out.append("| " + " | ".join(header) + " |")
    al = align or ["---"] * len(header)
    out.append("|" + "|".join(al) + "|")
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return "\n".join(out) + "\n"


TBL = {}
FACTS = {}


def put_table(name, text):
    assert text.startswith("*"), name
    TBL[name] = f"*Table {name}. " + text[1:]


def fact(name, value, source):
    if name in FACTS and FACTS[name][0] != value:
        raise ValueError(f"fact {name} defined twice with different values")
    FACTS[name] = (str(value), source)


def norm_cdf_upper(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


# ============================================================================= Section 0: headline

b053 = block("053")
b054 = block("054")
b055 = block("055")
L049 = {b["variant"]: b for b in blocks("049")}
L057 = {b["variant"]: b for b in blocks("057")}

fact("ho_ic", fnum(b054["cut_holdout_ic_mean"], 4), "run 054 cut_holdout_ic_mean")
fact("ho_ic3", fnum(b054["cut_holdout_ic_mean"], 3), "run 054 cut_holdout_ic_mean")
fact("ho_ic_t", fnum(b054["cut_holdout_ic_tstat_nw"], 2), "run 054 cut_holdout_ic_tstat_nw")
fact("ho_n", b054["cut_holdout_n_months"], "run 054 cut_holdout_n_months")
fact("iw_ic", fnum(b053["ic_mean"], 4), "run 053 ic_mean")
fact("iw_ic_t", fnum(b053["ic_tstat_nw"], 2), "run 053 ic_tstat_nw")
fact("iw_ic_plain_t", fnum(b053["ic_tstat"], 2), "run 053 ic_tstat")
fact("iw_ic_h1", fnum(b053["ic_half1_mean"], 4), "run 053 ic_half1_mean")
fact("iw_ic_h2", fnum(b053["ic_half2_mean"], 4), "run 053 ic_half2_mean")
fact("iw_n", b053["n_months"], "run 053 n_months")
fact("ho_raw_ret", fnum(b054["cut_holdout_ls_raw_ann_return_pct"], 2), "run 054 cut_holdout_ls_raw_ann_return_pct")
fact("ho_raw_ret1", fnum(b054["cut_holdout_ls_raw_ann_return_pct"], 1), "run 054 cut_holdout_ls_raw_ann_return_pct")
fact("ho_raw_sh", fnum(b054["cut_holdout_ls_raw_sharpe"], 2), "run 054 cut_holdout_ls_raw_sharpe")
fact("ho_h_ret", fnum(b054["cut_holdout_ls_ann_return_pct"], 2), "run 054 cut_holdout_ls_ann_return_pct")
fact("ho_h_sh", fnum(b054["cut_holdout_ls_sharpe"], 2), "run 054 cut_holdout_ls_sharpe")
fact("ho_h_t", fnum(b054["cut_holdout_ls_tstat_nw"], 2), "run 054 cut_holdout_ls_tstat_nw")
fact("ho_h_mdd", fnum(b054["cut_holdout_ls_maxdd_pct"], 2), "run 054 cut_holdout_ls_maxdd_pct")
fact("iw_h_ret", fnum(b053["ls_ann_return_pct"], 2), "run 053 ls_ann_return_pct")
fact("iw_h_sh", fnum(b053["ls_sharpe"], 3), "run 053 ls_sharpe")
fact("iw_h_t", fnum(b053["ls_tstat_nw"], 2), "run 053 ls_tstat_nw")
fact("iw_h_mdd", fnum(b053["ls_maxdd_pct"], 2), "run 053 ls_maxdd_pct")
fact("iw_raw_ret", fnum(b053["ls_raw_ann_return_pct"], 2), "run 053 ls_raw_ann_return_pct")
fact("iw_raw_sh", fnum(b053["ls_raw_sharpe"], 3), "run 053 ls_raw_sharpe")
fact("iw_raw_mdd", fnum(b053["ls_raw_maxdd_pct"], 2), "run 053 ls_raw_maxdd_pct")
hedge_iw = float(b053["ls_ann_return_pct"]) - float(b053["ls_raw_ann_return_pct"])
hedge_ho = float(b054["cut_holdout_ls_ann_return_pct"]) - float(b054["cut_holdout_ls_raw_ann_return_pct"])
fact("hedge_term_iw", fnum(hedge_iw, 2), "run 053 ls_ann_return_pct - ls_raw_ann_return_pct")
fact("hedge_term_ho", fnum(hedge_ho, 2), "run 054 cut_holdout_ls_ann_return_pct - cut_holdout_ls_raw_ann_return_pct")
fact("ho_beta_exante", fnum(b054["cut_holdout_ls_beta_mean"], 3), "run 054 cut_holdout_ls_beta_mean")
fact("ho_beta_exante2", fnum(b054["cut_holdout_ls_beta_mean"], 2), "run 054 cut_holdout_ls_beta_mean")
fact("ho_beta_real", fnum(b055["ls_beta_fullwindow"], 3), "run 055 ls_beta_fullwindow (holdout-only run, 57 months)")
fact("ho_beta_real2", fnum(b055["ls_beta_fullwindow"], 2), "run 055 ls_beta_fullwindow")
fact("ho_beta_exante_055", fnum(b055["ls_beta_mean"], 3), "run 055 ls_beta_mean")
fact("ho_beta_last", fnum(b054["ls_beta_last"], 3), "run 054 ls_beta_last")
lag = float(b054["cut_holdout_ls_beta_mean"]) - float(b055["ls_beta_fullwindow"])
fact("ho_beta_gap", fnum(lag, 3), "run 054 cut_holdout_ls_beta_mean - run 055 ls_beta_fullwindow")
fact("ho_beta_gap2", fnum(lag, 2), "run 054 cut_holdout_ls_beta_mean - run 055 ls_beta_fullwindow")
fact("iw_beta_exante", fnum(b053["ls_beta_mean"], 3), "run 053 ls_beta_mean")
fact("iw_beta_fw", fnum(b053["ls_beta_fullwindow"], 3), "run 053 ls_beta_fullwindow")
fact("iw_beta_fw2", fnum(b053["ls_beta_fullwindow"], 2), "run 053 ls_beta_fullwindow")
fact("layer_iw_gross_sh", fnum(L049["layer@100M"]["gross_sharpe"], 2), "run 049 layer@100M gross_sharpe")
fact("layer_iw_gross_sh3", fnum(L049["layer@100M"]["gross_sharpe"], 3), "run 049 layer@100M gross_sharpe")
fact("layer_iw057_gross_sh3", fnum(L057["layer@100M"]["cut_inwindow_gross_sharpe"], 3), "run 057 layer@100M cut_inwindow_gross_sharpe")
fact("layer_ho_gross_sh", fnum(L057["layer@100M"]["cut_holdout_gross_sharpe"], 2), "run 057 layer@100M cut_holdout_gross_sharpe")
fact("layer_ho_gross_ret", fnum(L057["layer@100M"]["cut_holdout_gross_ann_return_pct"], 2), "run 057 layer@100M cut_holdout_gross_ann_return_pct")
fact("layer_ho_net_sh", fnum(L057["layer@100M"]["cut_holdout_net_sharpe"], 2), "run 057 layer@100M cut_holdout_net_sharpe")
fact("layer_ho_net_ret", fnum(L057["layer@100M"]["cut_holdout_net_ann_return_pct"], 2), "run 057 layer@100M cut_holdout_net_ann_return_pct")
fact("ho_benchmark_h2", fnum(b053["ic_half2_mean"], 4), "run 053 ic_half2_mean (decision holdout_expectations_v14_spend_snapshot)")
fact("ho_ic_share_full", fnum(100 * float(b054["cut_holdout_ic_mean"]) / float(b053["ic_mean"]), 0),
     "100 x run 054 cut_holdout_ic_mean / run 053 ic_mean")

# layer rows: which are negative net of measured costs
pos_rows = []
for run, L, field in (("049", L049, "net_sharpe"), ("057 in-window", L057, "cut_inwindow_net_sharpe"),
                      ("057 holdout", L057, "cut_holdout_net_sharpe")):
    for var in sorted(L):
        if float(L[var][field]) > 0:
            pos_rows.append((run, var, L[var][field], L[var].get("half_spread_mode", "")))
canon_neg = all(float(L[f"layer@{a}M"][fld]) < 0 for a in ("100", "1000", "5000")
                for L, fld in ((L049, "net_sharpe"), (L057, "cut_inwindow_net_sharpe"), (L057, "cut_holdout_net_sharpe")))
fact("layer_canon_neg_all", "yes" if canon_neg else "no",
     "runs 049 net_sharpe, 057 cut_inwindow_net_sharpe and cut_holdout_net_sharpe for layer@100M/1000M/5000M")
put_table("07e_layer_positive_net_rows", table(
    ["run / window", "variant", "net Sharpe", "half-spread mode"],
    [(r, v, fnum(s, 3), m) for r, v, s, m in pos_rows],
    "Every construction-layer row with a positive net Sharpe. Source: runs 049 (`net_sharpe`), 057 "
    "(`cut_inwindow_net_sharpe`, `cut_holdout_net_sharpe`), all 33 variants each; `half_spread_mode` from the block."))
fact("n_pos_layer_rows", len(pos_rows), "count of rows in table 07e")
fact("n_pos_fixed", sum(1 for r in pos_rows if r[3] == "fixed"), "rows of table 07e with half_spread_mode fixed")
fact("n_pos_measured", sum(1 for r in pos_rows if r[3] == "measured"), "rows of table 07e with half_spread_mode measured")
fact("pos_measured_max", fnum(max(float(r[2]) for r in pos_rows if r[3] == "measured"), 3), "max net Sharpe over measured-spread rows of table 07e")
fact("n_pos_layer_rows_ho", sum(1 for r in pos_rows if r[0] == "057 holdout"), "count of 057 holdout rows in table 07e")

# ============================================================================= Section 1: pre-registration

run_started = [(i, e) for i, e in ev("run_started")]
cfg_shas = sorted({e["config_sha"] for _, e in run_started})
fact("config_sha", b053["config_sha"], "run 053 block config_sha")
fact("n_cfg_shas", len(cfg_shas), "distinct config_sha over every run_started event")
fact("n_runs_started", len(run_started), "run_started events")
fact("eval_start", CFG["dates"]["eval_start"], "config dates.eval_start")
fact("eval_end", CFG["dates"]["eval_end"], "config dates.eval_end")
fact("oos_start", CFG["dates"]["out_of_sample_start"], "config dates.out_of_sample_start")
fact("oos_end", CFG["dates"]["out_of_sample_end"], "config dates.out_of_sample_end")
fact("nw_lags", CFG["statistics"]["newey_west_lags"], "config statistics.newey_west_lags")
fact("beta_window", CFG["market_hedge"]["beta_window_months"], "config market_hedge.beta_window_months")
fact("beta_min", CFG["market_hedge"]["beta_min_months"], "config market_hedge.beta_min_months")
fact("min_names_group", CFG["ranking"]["min_names_per_group"], "config ranking.min_names_per_group")
fact("top_years_k", CFG["diagnostics"]["ex_regime_top_years"], "config diagnostics.ex_regime_top_years")
fact("mkt_state_lb", CFG["diagnostics"]["market_state_lookback_months"], "config diagnostics.market_state_lookback_months")
fact("families_max", CFG["search"]["families_max"], "config search.families_max")
fact("ladder_max", CFG["search"]["stage2_ladder_max_rungs"], "config search.stage2_ladder_max_rungs")
fact("s1_batch", CFG["search"]["stage1_batch_size"], "config search.stage1_batch_size")
fact("min_months", CFG["rebalance"]["min_months"], "config rebalance.min_months")
S1 = CFG["acceptance_thresholds"]["stage1_standalone"]
S2 = CFG["acceptance_thresholds"]["stage2_marginal"]
fact("bar_s1_t", fnum(S1["min_ic_tstat_nw"], 1), "config stage1_standalone.min_ic_tstat_nw")
fact("bar_s1_ic", fnum(S1["min_ic_mean"], 3), "config stage1_standalone.min_ic_mean")
fact("bar_s2_t", fnum(S2["min_resid_ic_tstat_nw"], 1), "config stage2_marginal.min_resid_ic_tstat_nw")
fact("bar_s2_guard", fnum(S2["min_paired_delta_ls_tstat"], 1), "config stage2_marginal.min_paired_delta_ls_tstat")
fact("osap_ref", CFG["osap_source"]["ref"][:8], "config osap_source.ref")

# the bars, verbatim from the config text
cfg_text = open(ROOT / "config/test_config.yaml").read().splitlines()
start = next(i for i, l in enumerate(cfg_text) if l.startswith("acceptance_thresholds:"))
end = next(i for i, l in enumerate(cfg_text) if l.startswith("search:"))
end2 = next(i for i in range(end + 1, len(cfg_text)) if cfg_text[i].startswith("# ----"))
bars = cfg_text[start:end2]
while bars and not bars[-1].strip():
    bars.pop()
assert not any(BANNED.search(l) for l in bars)
put_table("01_bars_verbatim",
          f"*The bars and the search rules, verbatim. Source: config/test_config.yaml lines {start + 1}-{end2} "
          f"(CONFIG_SHA {b053['config_sha']}).*\n\n```yaml\n" + "\n".join(bars) + "\n```\n")

# stop-and-ask, verbatim from CLAUDE.md
cl = open(ROOT / "CLAUDE.md").read().splitlines()
s = next(i for i, l in enumerate(cl) if l.startswith("### Stop and ask"))
items = []
for l in cl[s + 1:]:
    m = re.match(r"^(\d+)\. (.*)$", l)
    if m:
        items.append((m.group(1), m.group(2)))
    elif items and l.startswith("Everything else"):
        break
assert not any(BANNED.search(t) for _, t in items)
put_table("01b_stop_and_ask", table(["#", "stop and ask (verbatim)"], items,
                                    f"The stop-and-ask list. Source: CLAUDE.md lines {s + 2}-{s + 1 + len(items) + 1}."))

# D1..D11 headings
dec = open(ROOT / "docs/DECISIONS.md").read().splitlines()
PARA = {
    "D1": "Fresh project from an earlier project's skeleton: methodology and code by allow-list; no outcome carried; fresh data pull.",
    "D2": f"Windows: decisions {CFG['dates']['eval_start'][:7]}..{CFG['dates']['eval_end'][:7]}, holdout {CFG['dates']['out_of_sample_start'][:7]}..{CFG['dates']['out_of_sample_end'][:7]}; the holdout tests selection, not the construction change.",
    "D3": "Ranks formed within sector before the family blend; thin sector-months fall back to the cross-section; current sector label disclosed.",
    "D4": f"Long-short hedged to the universe's own cap-weighted return with an ex-ante {CFG['market_hedge']['beta_window_months']}-month beta; raw series and beta printed beside.",
    "D5": f"Beta and a date-free ex-regime Sharpe (ex top-{CFG['diagnostics']['ex_regime_top_years']} years; bear/bull by trailing {CFG['diagnostics']['market_state_lookback_months']}-month market) on every block and rung; never bars.",
    "D6": "Every other rule kept as pre-registered: bars, levels, family blend, universe, Stage 2 order and ladders, flip rule.",
    "D7": "What the construction layer must change before its first number: beta neutrality, a harness-built spread, regime cuts from the D5 rule.",
    "D8": "The holdout spend protocol: refresh, in-window reproduction, then one spend, read from cut_holdout_* fields.",
    "D9": "Version control local only until the owner publishes.",
    "D10": "Runner and advisor roles.",
    "D11": "The hedge reaches the Stage 2 guard only; the Stage 1 spread bar reads the raw D10-D1; no decile-monotonicity statistic.",
}
drows = []
for l in dec:
    m = re.match(r"^## (D\d+) — (\d{4}-\d{2}-\d{2}) — ", l)
    if m:
        did, date = m.group(1), m.group(2)
        own = re.search(r"\(owner: ([^;)]+)", l)
        drows.append((did, date, own.group(1) if own else "", PARA[did]))
dated_notes = [(l.split(" ")[1], re.search(r"process_finding (\S+)\)", l).group(1)) for l in dec if l.startswith("Note 2026")]
put_table("01c_decisions", table(["id", "date", "decided by", "what it fixes (paraphrase)"], drows,
                                  "Design decisions D1-D11. Source: docs/DECISIONS.md headings (id, date, owner); the right-hand column is a paraphrase. "
                                  f"Dated governing notes were added under D7 and D8 on {', '.join(sorted({d for d, _ in dated_notes}))} "
                                  f"(process_findings {', '.join(mask_id(x) for _, x in dated_notes)})."))
fact("n_decisions", len(drows), "docs/DECISIONS.md D headings")

# ============================================================================= Section 2: data

snaps = ev("snapshot_recorded")
srows = []
for i, e in snaps:
    sha = e.get("data_sha") or e.get("new_data_sha")
    old = e.get("old_data_sha", "(none)")
    tabs = e.get("tables")
    srows.append((i, e["ts"], old, sha, len(tabs) if tabs else "13 Sharadar + TB3MS (detail)",
                  safe_text(e.get("reason") or e.get("detail"), i, 260)))
put_table("02_snapshots", table(["events line", "ts (UTC)", "old DATA_SHA", "new DATA_SHA", "tables", "reason (record text)"], srows,
                                "The two snapshot recordings. Source: research/events.jsonl `snapshot_recorded` (record text truncated at 260 characters)."))
fact("data_sha_1", snaps[0][1]["data_sha"], "events snapshot_recorded #1 data_sha")
fact("data_sha_2", snaps[1][1]["new_data_sha"], "events snapshot_recorded #2 new_data_sha")
fact("n_sharadar_tables", len(snaps[0][1]["tables"]), "events snapshot_recorded #1 tables")
trows = []
for t in sorted(SNAP["tables"]):
    d = SNAP["tables"][t]
    trows.append((t, d.get("kind", "sharadar"), f"{d['rows']:,}", d.get("min_date", ""), d.get("max_date", "")))
put_table("02b_tables", table(["table", "kind", "rows", "min date", "max date"], trows,
                              f"Tables held in the spend snapshot. Source: data/SNAPSHOT_MANIFEST.yaml (status {SNAP['status']}, recorded_on {SNAP['recorded_on']}); "
                              "DATA_SHA is derived from the per-table sha256 values listed there."))
fact("snap2_recorded", SNAP["recorded_on"], "data/SNAPSHOT_MANIFEST.yaml recorded_on")
_, rf_dec = ev_one("decision", id="owner_stop_and_ask_3_approved")
fact("owner_sa3", rf_dec["verbatim"], "events decision owner_stop_and_ask_3_approved verbatim")
_, sa5 = ev_one("decision", id="owner_stop_and_ask_5_approved")
fact("owner_sa5", sa5["verbatim"], "events decision owner_stop_and_ask_5_approved verbatim")
fact("iw_rf_credit", fnum(b053["ls_rf_credit_pp"], 2), "run 053 ls_rf_credit_pp")
fact("iw_ex_sh", fnum(b053["ls_excess_sharpe"], 3), "run 053 ls_excess_sharpe")
fact("iw_ex_ret", fnum(b053["ls_excess_ann_return_pct"], 2), "run 053 ls_excess_ann_return_pct")
fact("iw_ex_t", fnum(b053["ls_excess_tstat_nw"], 2), "run 053 ls_excess_tstat_nw")
fact("iw_ex_top3", fnum(b053["ls_excess_sharpe_ex_top_years"], 3), "run 053 ls_excess_sharpe_ex_top_years")

# restatement 052 -> 053
b052 = block("052")
common = [k for k in b052 if k in b053]
same = [k for k in common if b052[k] == b053[k]]
moved = [k for k in common if b052[k] != b053[k]]
newk = [k for k in b053 if k not in b052]
fact("restate_same", len(same), "run 052 vs 053 result-block fields, identical")
fact("restate_moved", len(moved), "run 052 vs 053 result-block fields, different (includes data_sha)")
fact("restate_new", len(newk), "run 053 fields absent from 052 (the excess-of-rf diagnostic)")
rs_keys = ["ic_mean", "ic_tstat_nw", "ic_half1_mean", "ic_half2_mean", "ls_sharpe", "ls_ann_return_pct", "ls_tstat_nw",
           "ls_raw_sharpe", "ls_raw_ann_return_pct", "ls_beta_fullwindow", "ls_beta_mean", "ls_sharpe_ex_top_years",
           "ls_maxdd_pct", "turnover_d10_pct"]
put_table("02c_restatement", table(
    ["field", "run 052 (DATA 198b281de1a0)", "run 053 (DATA 42587e08609a)", "difference"],
    [(k, b052[k], b053[k], fsig(float(b053[k]) - float(b052[k]), 6)) for k in rs_keys],
    f"D8 step 2: the same harness, config and composite on the frozen and the refreshed bytes, in-window. Source: result blocks of runs 052 and 053; "
    f"{len(same)} fields identical, {len(moved)} different (including data_sha), {len(newk)} new in 053."))
fact("restate_dic", fsig(float(b053["ic_mean"]) - float(b052["ic_mean"]), 6), "run 053 ic_mean - run 052 ic_mean")
fact("restate_dt", fsig(float(b053["ic_tstat_nw"]) - float(b052["ic_tstat_nw"]), 4), "run 053 ic_tstat_nw - run 052 ic_tstat_nw")
fact("sh052", fnum(b052["ls_sharpe"], 3), "run 052 ls_sharpe")

# ============================================================================= Section 3: inventory and Stage 1

_, inv = ev_one("inventory_classified")
fact("n_osap", inv["n_predictors"], "events inventory_classified n_predictors")
fact("n_feasible", inv["n_feasible"], "events inventory_classified n_feasible")
fact("n_infeasible", inv["n_infeasible"], "events inventory_classified n_infeasible")
fact("n_translated", inv["n_translated"], "events inventory_classified n_translated")
fact("n_pf_failed", inv["n_preflight_failed"], "events inventory_classified n_preflight_failed")
fact("n_seed", inv["n_baseline_legs"], "events inventory_classified n_baseline_legs")
fclass = {}
for k in sorted(FRONT):
    fclass[FRONT[k]["class"]] = fclass.get(FRONT[k]["class"], 0) + 1
for c in fclass:
    assert fclass[c] == inv["by_reason"][c], (c, fclass[c], inv["by_reason"][c])
fact("n_frontier", len(FRONT), "osap_source/osap_frontier.yaml excluded rows")
for c, n in fclass.items():
    fact(f"n_fr_{c}", n, f"osap_frontier.yaml rows with class {c}")
s1_rows = {n: r for n, r in REG.items() if r.get("stage1_decision") in ("PASS", "FAIL")}
n_scr = len(s1_rows)
n_pass = sum(1 for r in s1_rows.values() if r["stage1_decision"] == "PASS")
assert n_scr == ACC["n_stage1_tested"] and n_pass == ACC["n_stage1_passed"]
fact("n_screened", n_scr, "registry rows with stage1_decision PASS/FAIL (= registry_index n_stage1_tested)")
fact("n_s1_pass", n_pass, "registry rows with stage1_decision PASS")
fact("n_s1_fail", n_scr - n_pass, "registry rows with stage1_decision FAIL")
fact("n_s1_incon", ACC["n_inconclusive"], "registry_index search_accounting n_inconclusive")
put_table("03_inventory", table(
    ["class", "count", "source"],
    [("OSAP predictors (SignalDoc Cat.Signal = Predictor, ref " + CFG["osap_source"]["ref"][:8] + ")", inv["n_predictors"], "inventory_classified"),
     ("seed legs (v0, never screened)", inv["n_baseline_legs"], "inventory_classified"),
     ("constructible: translated and preflight-passed", inv["n_translated"], "inventory_classified"),
     ("constructible: preflight failed (frontier class preflight_failed)", fclass.get("preflight_failed"), "osap_frontier.yaml"),
     ("not constructible: data unavailable in Sharadar (frontier class data_unavailable)", fclass.get("data_unavailable"), "osap_frontier.yaml"),
     ("not constructible: data start too late (frontier class data_start)", fclass.get("data_start"), "osap_frontier.yaml"),
     ("Stage 1 screens (translated candidates plus one declared flip)", n_scr, "registry rows"),
     ("Stage 1 passes", n_pass, "registry rows"),
     ("Stage 1 rejections", n_scr - n_pass, "registry rows"),
     ("Stage 1 inconclusive", ACC["n_inconclusive"], "registry_index")],
    "Inventory accounting. Sources: research/events.jsonl `inventory_classified`; osap_source/osap_frontier.yaml; research/registry/*.yaml; research/registry_index.yaml `search_accounting`."))

# failing bars
fail_dec = {}
fail_any = {}
for n, r in sorted(s1_rows.items()):
    if r["stage1_decision"] == "FAIL":
        fail_dec[r["decided_by"]] = fail_dec.get(r["decided_by"], 0) + 1
        for b in r.get("stage1_failed") or []:
            fail_any[b] = fail_any.get(b, 0) + 1
bar_names = sorted(set(fail_dec) | set(fail_any))
put_table("03b_stage1_fail_bars", table(
    ["bar", "decided the rejection", "failed (any position)"],
    [(b, fail_dec.get(b, 0), fail_any.get(b, 0)) for b in bar_names],
    "Stage 1 rejections by bar. Source: research/registry/*.yaml `decided_by` and `stage1_failed` on the FAIL rows "
    "(decided_by names ic_tstat_nw when it fails, else the first failed bar in check order: decisions stage1_decided_by_convention, _fallback)."))
fact("n_fail_by_t", fail_dec.get("ic_tstat_nw", 0), "registry FAIL rows decided_by ic_tstat_nw")

# t >= 2.5 but failed another bar
t_but_fail = sorted([(n, r["stage1"]["ic_tstat_nw"], r["stage1"]["ic_mean"], r["decided_by"]) for n, r in s1_rows.items()
                     if r["stage1_decision"] == "FAIL" and r["stage1"]["ic_tstat_nw"] >= S1["min_ic_tstat_nw"]], key=lambda x: -x[1])
put_table("03c_t_pass_other_fail", table(
    ["factor", "Stage 1 NW t", "mean IC", "decided by"],
    [(n, fnum(t, 4), fnum(ic, 4), d) for n, t, ic, d in t_but_fail],
    "Screens that cleared the t bar and failed another. Source: research/registry/<name>.yaml stage1.ic_tstat_nw, stage1.ic_mean, decided_by."))
fact("n_t_pass_other_fail", len(t_but_fail), "rows in table 03c")

# ---- the null calculation
n_osap_sign = sum(1 for n, r in s1_rows.items() if not n.endswith("Flip"))
n_flip_screens = n_scr - n_osap_sign
p25 = norm_cdf_upper(S1["min_ic_tstat_nw"])
FLIP_T = float(re.search(r"([\d.]+)", ev("flip_hypothesis_qualified")[0][1]["bar"]).group(1))
p274 = norm_cdf_upper(FLIP_T)
p20 = norm_cdf_upper(S2["min_resid_ic_tstat_nw"])
e1 = n_osap_sign * p25
e2 = n_osap_sign * p274
n_s2 = ACC["n_stage2_tested"]
e3 = n_s2 * p20
obs_t25 = sum(1 for n, r in s1_rows.items() if not n.endswith("Flip") and r["stage1"]["ic_tstat_nw"] >= S1["min_ic_tstat_nw"])
obs_neg274 = len(ev("flip_hypothesis_qualified"))
n_acc = ACC["n_accepted"]
put_table("03d_null_fp", table(
    ["test family", "tests n", "bar", "tail", "p = P(Z beyond bar)", "expected false positives n x p", "observed"],
    [("Stage 1, published sign", n_osap_sign, f"NW t >= {fnum(S1['min_ic_tstat_nw'], 2)}", "one-sided (upper)", fnum(p25, 6), fnum(e1, 3),
      f"{obs_t25} with t >= bar; {n_pass - n_flip_screens} passed every bar"),
     ("Stage 1, flip qualification (reversed sign)", n_osap_sign, f"NW t <= -{fnum(FLIP_T, 2)}", "one-sided (lower)", fnum(p274, 6), fnum(e2, 3),
      f"{obs_neg274} qualified, {n_flip_screens} screened and passed"),
     ("Stage 1, both paths", n_osap_sign, "", "", fnum(p25 + p274, 6), fnum(e1 + e2, 3), f"{n_pass} passed"),
     ("Stage 2, residual IC", n_s2, f"NW t > {fnum(S2['min_resid_ic_tstat_nw'], 2)}", "one-sided (upper)", fnum(p20, 6), fnum(e3, 3), f"{n_acc} accepted")],
    "Expected false positives under the global null. Normal tail, p = 0.5 erfc(z / sqrt 2); counts from research/registry/*.yaml and "
    "research/registry_index.yaml `search_accounting`; bars from config/test_config.yaml; the 2.74 flip bar from CLAUDE.md and events "
    "`flip_hypothesis_qualified`. The expectation n x p holds under any dependence between tests; dependence widens its spread."))
fact("null_n", n_osap_sign, "registry Stage 1 rows in the published sign")
fact("null_p25", fnum(p25, 6), "0.5 erfc(2.5/sqrt 2)")
fact("null_e1", fnum(e1, 3), "null_n x null_p25")
fact("null_p274", fnum(p274, 6), "0.5 erfc(2.74/sqrt 2)")
fact("null_e2", fnum(e2, 3), "null_n x null_p274")
fact("null_etot", fnum(e1 + e2, 3), "null_e1 + null_e2")
fact("null_p20", fnum(p20, 6), "0.5 erfc(2.0/sqrt 2)")
fact("null_e3", fnum(e3, 3), "n_stage2_tested x null_p20")
fact("null_obs_t25", obs_t25, "registry Stage 1 rows (published sign) with ic_tstat_nw >= 2.5")
fact("n_flip_screens", n_flip_screens, "registry Stage 1 rows named *Flip")
fact("n_flip_qualified", obs_neg274, "events flip_hypothesis_qualified")
fact("flip_bar", fnum(FLIP_T, 2), "CLAUDE.md flip rule |t| >= 2.74")

# flips
frows = []
for i, e in ev("flip_hypothesis_qualified"):
    fl = e["flipped_name"]
    screened = fl in REG
    st = REG[fl]["stage1"]["ic_tstat_nw"] if screened else None
    frows.append((i, e["factor"], fnum(e["stats_osap_sign"]["ic_tstat_nw"], 4), fnum(e["stats_osap_sign"]["ic_mean"], 6), fl,
                  "yes (run " + REG[fl]["run"] + ")" if screened else "no",
                  fnum(st, 4) if screened else "", (REG[fl]["stage1_decision"] + " / " + REG[fl]["status"]) if screened else
                  "not screened (decision flip_not_screened_when_deterministic_fail: reversed IC below the 0.010 bar)"))
put_table("03e_flips", table(
    ["events line", "parent", "parent NW t", "parent mean IC", "flip", "screened", "flip Stage 1 NW t", "outcome"], frows,
    "Flip hypotheses. Source: events `flip_hypothesis_qualified` (parent statistics), research/registry/<flip>.yaml (screen), "
    "decision flip_not_screened_when_deterministic_fail."))
fact("bas_flip_t", fnum(REG["BidAskSpreadFlip"]["stage1"]["ic_tstat_nw"], 4), "registry BidAskSpreadFlip stage1.ic_tstat_nw")
fact("bas_flip_t2", fnum(REG["BidAskSpreadFlip"]["stage1"]["ic_tstat_nw"], 2), "registry BidAskSpreadFlip stage1.ic_tstat_nw")
fact("bas_parent_t", fnum(abs(ev_one("flip_hypothesis_qualified", factor="BidAskSpread")[1]["stats_osap_sign"]["ic_tstat_nw"]), 2),
     "events flip_hypothesis_qualified BidAskSpread |ic_tstat_nw|")
fact("grl_parent_t", fnum(abs(ev_one("flip_hypothesis_qualified", factor="GrLTNOA")[1]["stats_osap_sign"]["ic_tstat_nw"]), 2),
     "events flip_hypothesis_qualified GrLTNOA |ic_tstat_nw|")
fact("grl_rev_ic", fnum(abs(ev_one("flip_hypothesis_qualified", factor="GrLTNOA")[1]["stats_osap_sign"]["ic_mean"]), 4),
     "events flip_hypothesis_qualified GrLTNOA |ic_mean|")

# ============================================================================= Section 4: families and order

_, part = ev_one("decision", id="phase_c_family_partition")
m = re.search(r"map fixed before any assignment: (.*?)\. 9 families", part["decision"])
pairs = [tuple(x.strip().split("->")) for x in m.group(1).split(";")]
passer_labels = {}
for a in FAM["assignments"]:
    passer_labels.setdefault(a["cat_economic"], []).append(a["factor"])
seed_map = {"size": "size"}
lrows = [("size", "size", "seed (v0 Size)", "")]
for lab, famname in pairs:
    famname = re.sub(r"\s*\(new\)$", "", famname.strip())
    lrows.append((lab, famname, "seed family" if famname in ("size", "value", "profitability", "investment", "momentum") else "new family",
                  ", ".join(passer_labels.get(lab, []))))
labels = sorted({r[0] for r in lrows})
fact("n_labels", len(labels), "distinct SignalDoc Cat.Economic labels in table 04 (seed labels plus passer labels)")
fact("n_families", len({r[1] for r in lrows}), "distinct families in table 04")
put_table("04_label_map", table(
    ["SignalDoc Cat.Economic label", "family", "family kind", "Stage 1 passers carrying the label"], lrows,
    "Label-to-family map fixed before any assignment. Source: events decision phase_c_family_partition (map text, parsed), "
    "research/families.yaml `assignments` (passers per label). The size row is the v0 seed; no passer carries that label."))

v14fam = {}
for chunk in VER["v14"]["families"].split("|"):
    f, members = chunk.split(":")
    v14fam[f] = members.split(",")
frows2 = []
for f, d in FAM["families"].items():
    frows2.append((f, d["definition"], len(d["members"]), ", ".join(d["members"]), ", ".join(v14fam.get(f, []))))
put_table("04b_families", table(["family", "definition", "members", "members (seeds first, passers in assignment order)", "in v14"], frows2,
                                "The nine families. Source: research/families.yaml `families`; the v14 column from MODEL_MANIFEST.yaml v14 `families`."))
# timeline
last_s1 = ev_one("run_completed", seq="011")
phB = ev_one("phase_completed", phase="B")
fa = ev("family_assigned")
so = ev_one("stage2_order_declared")
phC = ev_one("phase_completed", phase="C")
first_s2 = ev_one("run_started", seq="012")
first_s2_num = min((i, e) for i, e in ev("factor_evaluated") if e.get("stage") == 2)
trow = [("last Stage 1 run completed (run 011)", last_s1[0], last_s1[1]["ts"]),
        ("phase B closed", phB[0], phB[1]["ts"]),
        (f"first and last of {len(fa)} family_assigned", f"{fa[0][0]}-{fa[-1][0]}", f"{fa[0][1]['ts']} / {fa[-1][1]['ts']}"),
        ("stage2_order_declared", so[0], so[1]["ts"]),
        ("research/stage2_order.yaml `declared`", "", ORD["declared"]),
        ("phase C closed", phC[0], phC[1]["ts"]),
        ("first Stage 2 run started (run 012)", first_s2[0], first_s2[1]["ts"]),
        ("first Stage 2 number evaluated (factor_evaluated, run 012)", first_s2_num[0], first_s2_num[1]["ts"])]
assert fa[-1][1]["ts"] <= first_s2[1]["ts"] and so[1]["ts"] < first_s2[1]["ts"]
put_table("04c_phase_c_timeline", table(["event", "events line", "ts (UTC)"], trow,
                                        "Phase C closed before any Stage 2 number. Source: research/events.jsonl, research/stage2_order.yaml."))
fact("n_family_assigned", len(fa), "events family_assigned")
# families_max reached
reach = next(v for v in VORDER if len(VER[v]["families"].split("|")) == CFG["search"]["families_max"])
fact("fmax_reached", reach, "first MODEL_MANIFEST version whose families string has families_max entries")

ordrows = [(o["rank"], o["factor"], fnum(o["ic_tstat_nw"], 6), fnum(o["ic_mean"], 6), o["family"]) for o in ORD["order"]]
put_table("A4_stage2_order", table(["rank", "factor", "Stage 1 NW t", "Stage 1 mean IC", "family"], ordrows,
                                   f"The pre-declared Stage 2 order (rule {ORD['rule']}, declared {ORD['declared']}). Source: research/stage2_order.yaml."))
put_table("A3_families_yaml", "*research/families.yaml, verbatim.*\n\n```yaml\n" + open(ROOT / "research/families.yaml").read().rstrip() + "\n```\n")

# ============================================================================= Section 5: the ratchet

ver_of = {}
for v in VORDER:
    r = VER[v].get("ratchet")
    if r:
        added = [l["name"] for l in VER[v]["legs"]][-1]
        ver_of[added] = v
ladder_runs = sorted({REG[o["factor"]]["stage2_run"] for o in ORD["order"]})
fact("ladder_runs", ", ".join(ladder_runs), "registry stage2_run over the 24 Stage 2 rows")
fact("n_ladders", len(ladder_runs), "distinct stage2_run")
rrows = []
s2 = []
for o in ORD["order"]:
    r = REG[o["factor"]]
    st = r["stage2"]
    nbase = len(st["base_legs"].split(","))
    s2.append((o["factor"], r, st))
    rrows.append((r["stage2_run"], st["ratchet_order"], o["rank"], o["factor"], r["family"], nbase,
                  fnum(st["resid_ic_mean"], 4), fnum(st["resid_ic_tstat_nw"], 6), st["resid_ic_n"],
                  fnum(st["paired_delta_ls_tstat"], 4), fnum(st["paired_delta_ic_tstat"], 2), st["ratchet_decision"],
                  r["decided_by"], ver_of.get(o["factor"], "")))
put_table("05_rungs", table(
    ["run", "rung", "order rank", "factor", "family", "base legs", "resid IC", "resid IC NW t (bar > 2.0)", "resid months",
     "guard t (bar >= -2.0)", "paired dIC t (diag.)", "verdict", "decided by", "version"], rrows,
    "Every Stage 2 rung. Source: research/registry/<name>.yaml `stage2_run`, `stage2` (verbatim from the rung's block), `decided_by`; "
    "version from MODEL_MANIFEST.yaml `ratchet`. Acceptance-time, pre-refresh bytes (DATA 198b281de1a0)."))
n_s2_acc = sum(1 for _, r, st in s2 if st["ratchet_decision"] == "PASS")
n_s2_rej = sum(1 for _, r, st in s2 if st["ratchet_decision"] == "FAIL")
assert n_s2_acc == ACC["n_accepted"]
rej_bars = sorted({r["decided_by"] for _, r, st in s2 if st["ratchet_decision"] == "FAIL"})
guard_fail = sum(1 for _, r, st in s2 if st["paired_delta_ls_tstat"] < S2["min_paired_delta_ls_tstat"])
fact("n_s2", len(s2), "Stage 2 rows")
fact("n_s2_acc", n_s2_acc, "Stage 2 rows ratchet_decision PASS")
fact("n_s2_rej", n_s2_rej, "Stage 2 rows ratchet_decision FAIL")
fact("n_s2_incon", ACC["n_inconclusive"], "registry_index n_inconclusive")
fact("s2_rej_bars", ", ".join(rej_bars), "decided_by over Stage 2 FAIL rows")
fact("n_guard_fail", guard_fail, "Stage 2 rows with paired_delta_ls_tstat < -2.0")
min_guard = min(s2, key=lambda x: x[2]["paired_delta_ls_tstat"])
fact("min_guard_t", fnum(min_guard[2]["paired_delta_ls_tstat"], 2), f"registry {min_guard[0]} stage2.paired_delta_ls_tstat (lowest guard t)")
fact("min_guard_f", min_guard[0], "factor with the lowest guard t")
tal = []
for run in ladder_runs:
    rr = [(f, st) for f, r, st in s2 if r["stage2_run"] == run]
    acc = [f for f, st in rr if st["ratchet_decision"] == "PASS"]
    rej = [f for f, st in rr if st["ratchet_decision"] == "FAIL"]
    base = rr[0][1]["base_legs"].split(",")
    tal.append((run, len(rr), len(base), len(acc), len(rej), ", ".join(acc), ", ".join(rej)))
put_table("05b_ladders", table(["run", "rungs", "legs in base at rung 1", "accepted", "rejected", "accepted factors", "rejected factors"], tal,
                               "Ladder tallies. Source: research/registry/*.yaml stage2 rows grouped by `stage2_run`."))
passes = sorted([(st["resid_ic_tstat_nw"] - S2["min_resid_ic_tstat_nw"], f, st) for f, r, st in s2 if st["ratchet_decision"] == "PASS"])
misses = sorted([(S2["min_resid_ic_tstat_nw"] - st["resid_ic_tstat_nw"], f, st) for f, r, st in s2 if st["ratchet_decision"] == "FAIL"])
mrows = [("thinnest pass", f, fnum(st["resid_ic_tstat_nw"], 6), fsig(m_, 6)) for m_, f, st in passes[:3]] + \
        [("nearest miss", f, fnum(st["resid_ic_tstat_nw"], 6), fsig(-m_, 6)) for m_, f, st in misses[:3]]
put_table("05c_margins", table(["kind", "factor", "resid IC NW t", "margin to 2.0"], mrows,
                               "Thinnest passes and nearest misses on the residual-IC bar. Source: research/registry/<name>.yaml stage2.resid_ic_tstat_nw."))
for k, (m_, f, st) in enumerate(passes[:2]):
    fact(f"thin{k}", f, "table 05c")
    fact(f"thin{k}_t", fnum(st["resid_ic_tstat_nw"], 2), f"registry {f} stage2.resid_ic_tstat_nw")
for k, (m_, f, st) in enumerate(misses[:2]):
    fact(f"miss{k}", f, "table 05c")
    fact(f"miss{k}_t", fnum(st["resid_ic_tstat_nw"], 2), f"registry {f} stage2.resid_ic_tstat_nw")

# hedge-guard property
_, hg = ev_one("decision", id="hedge_guard_negative_beta_property")
_, mr = ev_one("factor_evaluated", factor="MaxRet", stage=2)
fact("mr_hedged_dls", fnum(mr["raw_vs_hedged_dls_pp"]["hedged"], 2), "events factor_evaluated MaxRet stage 2 raw_vs_hedged_dls_pp.hedged")
fact("mr_raw_dls", fnum(mr["raw_vs_hedged_dls_pp"]["raw"], 2), "events factor_evaluated MaxRet raw_vs_hedged_dls_pp.raw")
fact("mr_hedge_part", fnum(mr["raw_vs_hedged_dls_pp"]["hedge_part"], 2), "events factor_evaluated MaxRet raw_vs_hedged_dls_pp.hedge_part")
fact("mr_resid_t", fnum(REG["MaxRet"]["stage2"]["resid_ic_tstat_nw"], 2), "registry MaxRet stage2.resid_ic_tstat_nw")
hgrows = []
for i, e in ev("factor_evaluated"):
    if e.get("stage") == 2 and "raw_vs_hedged_dls_pp" in e:
        d = e["raw_vs_hedged_dls_pp"]
        hgrows.append((e["seq"], e["factor"], fsig(d["raw"], 2), fsig(d["hedge_part"], 2), fsig(d["hedged"], 2),
                       fnum(e["stats"]["paired_delta_ls_tstat"], 2), e["decision"]))
put_table("05d_hedge_part", table(["run", "factor", "raw dLS pp/yr", "hedge part pp/yr", "hedged dLS pp/yr", "guard t", "verdict"], hgrows,
                                  "The guard's delta split into raw spread and hedge term, as recorded from ladder 2 on. Source: events "
                                  "`factor_evaluated` (stage 2) field raw_vs_hedged_dls_pp; ladder 1 rows predate the field."))

_, phD = ev_one("phase_completed", phase="D")
fact("repro_fields", re.search(r"(\d+/\d+) fields", phD["digest"]).group(1), "events phase_completed D digest")

# version table (acceptance-time)
vrows = []
for v in VORDER:
    V = VER[v]
    bl = V["baseline"]
    r = V.get("ratchet") or {}
    added = V["legs"][-1]["name"] if r else "(seed: " + ", ".join(l["name"] for l in V["legs"]) + ")"
    fam_added = V["legs"][-1]["family"] if r else ""
    nf = len(V["families"].split("|"))
    vrows.append((v, added, fam_added, len(V["legs"]), nf,
                  (r.get("run", "") + "/" + str(r.get("rung", ""))) if r else "",
                  fnum(r["bars"]["resid_ic_tstat_nw"], 2) if r else "", fnum(r["bars"]["paired_delta_ls_tstat"], 2) if r else "",
                  bl["run"], fnum(bl["ic"]["ic_mean"], 4), fnum(bl["ic"]["ic_tstat_nw"], 2),
                  fnum(bl["ls_hedged"]["ls_sharpe"], 3), fnum(bl["ls_hedged"]["ls_ann_return_pct"], 2), fnum(bl["ls_hedged"]["ls_maxdd_pct"], 2),
                  fnum(bl["beta"]["ls_beta_fullwindow"], 3), fnum(bl["ls_raw"]["ls_raw_sharpe"], 3),
                  fnum(bl["ex_regime"]["ls_sharpe_ex_top_years"], 3), fnum(bl["breadth"]["turnover_d10_pct"], 1), V["construction"]["run"],
                  V["stamps"]["composite_sha"]))
VH = ["version", "leg added", "family", "legs", "families", "ratchet run/rung", "resid t", "guard t", "baseline run", "IC", "IC NW t",
      "hedged Sharpe", "hedged ann %", "hedged MaxDD %", "beta (full window)", "raw Sharpe", "Sharpe ex top-3 yrs", "D10 turnover %", "Stage 3 run",
      "COMPOSITE_SHA"]
put_table("05e_versions", table(VH, vrows,
                                "Version history v0-v14, acceptance-time, pre-refresh bytes (DATA 198b281de1a0). Source: MODEL_MANIFEST.yaml `versions[*]` "
                                "(`legs`, `families`, `ratchet.bars`, `baseline`, `construction.run`, `stamps`). Gross; LS hedged unless labelled raw."))
v0b, v14b = VER["v0"]["baseline"], VER["v14"]["baseline"]
fact("v0_ic", fnum(v0b["ic"]["ic_mean"], 4), "manifest v0 baseline.ic.ic_mean (run 001)")
fact("v0_ic_t", fnum(v0b["ic"]["ic_tstat_nw"], 2), "manifest v0 baseline.ic.ic_tstat_nw (run 001)")
fact("v0_sh", fnum(v0b["ls_hedged"]["ls_sharpe"], 3), "manifest v0 baseline.ls_hedged.ls_sharpe (run 001)")
fact("v0_beta", fnum(v0b["beta"]["ls_beta_fullwindow"], 3), "manifest v0 baseline.beta.ls_beta_fullwindow (run 001)")
fact("v0_to", fnum(v0b["breadth"]["turnover_d10_pct"], 1), "manifest v0 baseline.breadth.turnover_d10_pct (run 001)")
fact("v14a_ic", fnum(v14b["ic"]["ic_mean"], 4), "manifest v14 baseline.ic.ic_mean (run 042)")
fact("v14a_ic_t", fnum(v14b["ic"]["ic_tstat_nw"], 2), "manifest v14 baseline.ic.ic_tstat_nw (run 042)")
fact("v14a_sh", fnum(v14b["ls_hedged"]["ls_sharpe"], 3), "manifest v14 baseline.ls_hedged.ls_sharpe (run 042)")
fact("v14a_beta", fnum(v14b["beta"]["ls_beta_fullwindow"], 3), "manifest v14 baseline.beta.ls_beta_fullwindow (run 042)")
fact("v14a_to", fnum(v14b["breadth"]["turnover_d10_pct"], 1), "manifest v14 baseline.breadth.turnover_d10_pct (run 042)")
_best = max(VORDER, key=lambda v: VER[v]["baseline"]["ls_hedged"]["ls_sharpe"])
fact("best_sh_ver", _best, "manifest version with the highest baseline.ls_hedged.ls_sharpe")
fact("best_sh", fnum(VER[_best]["baseline"]["ls_hedged"]["ls_sharpe"], 3), f"manifest {_best} baseline.ls_hedged.ls_sharpe")
fact("v14_legs", len(VER["v14"]["legs"]), "manifest v14 legs")
fact("v14_fams", len(VER["v14"]["families"].split("|")), "manifest v14 families")
fact("v14_sha", VER["v14"]["stamps"]["composite_sha"], "manifest v14 stamps.composite_sha")

# manifest headline appendix (acceptance-time plus the v14 restatement and holdout)
a5 = []
for v in VORDER:
    V = VER[v]
    bl = V["baseline"]
    a5.append((v, bl["run"], "acceptance-time (DATA " + V["stamps"]["data_sha"] + ")", len(V["legs"]), len(V["families"].split("|")),
               fnum(bl["ic"]["ic_mean"], 4), fnum(bl["ic"]["ic_tstat_nw"], 2), fnum(bl["ls_hedged"]["ls_sharpe"], 3),
               fnum(bl["ls_hedged"]["ls_ann_return_pct"], 2), fnum(bl["ls_hedged"]["ls_maxdd_pct"], 2), fnum(bl["beta"]["ls_beta_fullwindow"], 3),
               fnum(bl["breadth"]["turnover_d10_pct"], 1)))
a5.append(("v14", "053", "in-window, spend snapshot (DATA " + b053["data_sha"] + ")", len(VER["v14"]["legs"]), len(VER["v14"]["families"].split("|")),
           fnum(b053["ic_mean"], 4), fnum(b053["ic_tstat_nw"], 2), fnum(b053["ls_sharpe"], 3), fnum(b053["ls_ann_return_pct"], 2),
           fnum(b053["ls_maxdd_pct"], 2), fnum(b053["ls_beta_fullwindow"], 3), fnum(b053["turnover_d10_pct"], 1)))
a5.append(("v14", "054 (055 for beta, turnover)", "holdout " + CFG["dates"]["out_of_sample_start"][:7] + ".." + CFG["dates"]["out_of_sample_end"][:7],
           len(VER["v14"]["legs"]), len(VER["v14"]["families"].split("|")),
           fnum(b054["cut_holdout_ic_mean"], 4), fnum(b054["cut_holdout_ic_tstat_nw"], 2), fnum(b054["cut_holdout_ls_sharpe"], 3),
           fnum(b054["cut_holdout_ls_ann_return_pct"], 2), fnum(b054["cut_holdout_ls_maxdd_pct"], 2), fnum(b055["ls_beta_fullwindow"], 3),
           fnum(b055["turnover_d10_pct"], 1)))
put_table("A5_manifest_headlines", table(
    ["version", "run", "window and bytes", "legs", "families", "mean IC", "IC t (NW)", "LS Sharpe", "ann ret %", "MaxDD %", "beta", "turnover %"], a5,
    "Manifest headlines v0-v14 in the project's summary format (Sharpe, return and MaxDD hedged; beta the full-window beta of the raw LS; "
    "turnover D10 per month). Sources: MODEL_MANIFEST.yaml `versions[*].baseline`; run 053; run 054 `cut_holdout_*` and run 055 "
    "(`ls_beta_fullwindow`, `turnover_d10_pct`) for the holdout row."))

# tags
trows = []
for v in VORDER:
    t = MAN["tags"][v]
    trows.append((v, t["tag"], t["commit"], t.get("version_commit", ""), "MIS-POINTED (owner decides)" if t.get("mispointed") else ""))
put_table("A6_tags", table(["version", "tag", "tag commit", "version commit (if different)", "note"], trows,
                           "Tag-to-commit map. Source: MODEL_MANIFEST.yaml `tags` (built from `git tag -l 'v*'` and `git rev-parse <tag>^{commit}`)."))

# ============================================================================= Section 6: the in-window composite (run 053)

hl = [("mean IC", fnum(b053["ic_mean"], 4)), ("IC NW t (plain t)", f"{fnum(b053['ic_tstat_nw'], 2)} ({fnum(b053['ic_tstat'], 2)})"),
      ("ICIR", fnum(b053["icir"], 3)), ("IC halves", f"{fnum(b053['ic_half1_mean'], 4)} / {fnum(b053['ic_half2_mean'], 4)}"),
      ("IC > 0 months %", fnum(b053["ic_pct_positive"], 1)),
      ("hedged LS ann % / vol % / Sharpe / NW t", f"{fnum(b053['ls_ann_return_pct'], 2)} / {fnum(b053['ls_ann_vol_pct'], 2)} / {fnum(b053['ls_sharpe'], 3)} / {fnum(b053['ls_tstat_nw'], 2)}"),
      ("hedged MaxDD %", fnum(b053["ls_maxdd_pct"], 2)), ("hit rate %", fnum(b053["ls_hit_rate_pct"], 1)),
      ("raw LS ann % / vol % / Sharpe / MaxDD %", f"{fnum(b053['ls_raw_ann_return_pct'], 2)} / {fnum(b053['ls_raw_ann_vol_pct'], 2)} / {fnum(b053['ls_raw_sharpe'], 3)} / {fnum(b053['ls_raw_maxdd_pct'], 2)}"),
      ("excess-of-rf hedged ann % / Sharpe / NW t (diagnostic)", f"{fnum(b053['ls_excess_ann_return_pct'], 2)} / {fnum(b053['ls_excess_sharpe'], 3)} / {fnum(b053['ls_excess_tstat_nw'], 2)}"),
      ("rf credit pp/yr", fnum(b053["ls_rf_credit_pp"], 3)),
      ("beta ex ante (mean) / full window", f"{fnum(b053['ls_beta_mean'], 3)} / {fnum(b053['ls_beta_fullwindow'], 3)}"),
      ("hedged months", b053["ls_hedged_months"]),
      ("Sharpe ex top-3 years (years)", f"{fnum(b053['ls_sharpe_ex_top_years'], 3)} ({b053['ls_top_years']})"),
      ("top-3 years' share of summed LS %", fnum(b053["ls_top_years_share_pct"], 1)),
      ("Sharpe bear / bull (months)", f"{fnum(b053['ls_sharpe_bear'], 3)} / {fnum(b053['ls_sharpe_bull'], 3)} ({b053['n_bear_months']} / {b053['n_bull_months']})"),
      ("IC decay h1 / h3 / h6 / h12", " / ".join(fnum(b053[f"ic_decay_h{h}"], 4) for h in (1, 3, 6, 12))),
      ("D10 / D1 turnover % per month", f"{fnum(b053['turnover_d10_pct'], 1)} / {fnum(b053['turnover_d1_pct'], 1)}"),
      ("names per decile", fnum(b053["avg_names_per_decile"], 1)),
      ("names with all legs scored %", fnum(b053["leg_coverage_pct_full"], 1)),
      ("delisting-adjusted returns %", fnum(b053["delisting_adjusted_pct"], 2))]
put_table("06_v14_inwindow", table(["statistic", "value"], hl,
                                   "v14 in-window, 1999-01..2021-12, on the spend snapshot. Source: run 053 result block (HARNESS 1271266472a9, CONFIG 0d88328d5b10, "
                                   "COMPOSITE 7fe6f001e708, DATA 42587e08609a). Gross; LS hedged unless labelled raw."))
fact("iw_top_years", b053["ls_top_years"], "run 053 ls_top_years")
fact("iw_top3", fnum(b053["ls_sharpe_ex_top_years"], 3), "run 053 ls_sharpe_ex_top_years")
fact("iw_top_share", fnum(b053["ls_top_years_share_pct"], 1), "run 053 ls_top_years_share_pct")
fact("iw_bear", fnum(b053["ls_sharpe_bear"], 3), "run 053 ls_sharpe_bear")
fact("iw_bull", fnum(b053["ls_sharpe_bull"], 3), "run 053 ls_sharpe_bull")
fact("iw_to", fnum(b053["turnover_d10_pct"], 1), "run 053 turnover_d10_pct")
fact("iw_mdd", fnum(b053["ls_maxdd_pct"], 2), "run 053 ls_maxdd_pct")
dec053 = b053["decile_avg_ret_pct"].split(",")
dec055 = b055["decile_avg_ret_pct"].split(",")
put_table("06b_deciles", table(["decile"] + [f"D{k}" for k in range(1, 11)],
                               [("in-window raw %/mo (run 053)",) + tuple(dec053), ("holdout raw %/mo (run 055)",) + tuple(dec055)],
                               "Decile mean monthly returns, equal weight, raw. Source: `decile_avg_ret_pct` in the run 053 block (1999-2021) and the run 055 "
                               "block (holdout-only, 2022-01..2026-09; run 054's holdout cut prints no deciles)."))
tiers = [(t, b053[f"tier_{t}_ic_mean"], b053[f"tier_{t}_ls_sharpe"], b053[f"tier_{t}_avg_n"]) for t in ("MEGA", "MID", "SMALL")]
put_table("06c_tiers", table(["tier", "IC", "raw LS Sharpe", "avg names"], tiers,
                             "Liquidity tiers in-window (diagnostic). Source: run 053 `tier_*` fields."))
ai = annual_pairs(summary_line("053", "annual IC:"))
put_table("06d_annual_ic", table(["year"] + [str(y) for y, _ in ai[:12]], [("IC",) + tuple(fsig(v, 3) for _, v in ai[:12])],
                                 "Annual mean IC, in-window, part 1. Source: research/results/053_*_summary.md `annual IC`.") + "\n" +
          table(["year"] + [str(y) for y, _ in ai[12:]], [("IC",) + tuple(fsig(v, 3) for _, v in ai[12:])],
                "Annual mean IC, in-window, part 2. Source: as above."))
fact("n_neg_ic_years", sum(1 for _, v in ai if v < 0), "run 053 summary annual IC < 0")
fact("n_ic_years", len(ai), "run 053 summary annual IC years")

# legs active by year
cover = preflight_cover("053", "1998-12-31")
legs = [l["name"] for l in VER["v14"]["legs"]]
fam_of = {l["name"]: l["family"] for l in VER["v14"]["legs"]}
first = {}
for leg in legs:
    if leg in REG and REG[leg].get("stage1"):
        n = REG[leg]["stage1"]["n_months"]
    else:
        assert cover.get(leg, 0) > 0, leg
        n = int(b053["n_months"])
    k = int(b053["n_months"]) - n  # leading unscored months
    y, mo = 1999 + k // 12, 1 + k % 12
    first[leg] = (n, f"{y}-{mo:02d}")
lrows = []
for leg in legs:
    n, fm = first[leg]
    y, mo = map(int, fm.split("-"))
    sm = f"{y - (1 if mo == 1 else 0)}-{(12 if mo == 1 else mo - 1):02d}"
    lrows.append((leg, fam_of[leg], n, fm, sm, fnum(cover.get(leg, 0.0), 1)))
put_table("06e_leg_starts", table(["leg", "family", "scored months", "first holding month", "first signal month-end", "coverage at the 1998-12-31 probe %"], lrows,
                                  "When each v14 leg starts. Source: research/registry/<leg>.yaml stage1.n_months (candidates) and the run 053 preflight table "
                                  "(1998-12-31 probe); seed legs have no Stage 1 row and score from the first month. First month = 1999-01 plus "
                                  "(276 - scored months), i.e. unscored months are leading; registry caveats give the reasons (IdioVol3F: FF3 factors from "
                                  "1999-07; ShareIss5Y: 65-month history gate; VolumeTrend: 60-month window; TrendFactor: uncensored coefficients from 2002-12)."))
yrows = []
for y in range(1999, 2022):
    def active(leg, mo):
        fy, fmo = map(int, first[leg][1].split("-"))
        return (y, mo) >= (fy, fmo)
    jan = [l for l in legs if active(l, 1)]
    dec_ = [l for l in legs if active(l, 12)]
    if y == 1999 or len(jan) != len(dec_) or (yrows and yrows[-1][2] != len(jan)):
        yrows.append((y, len(jan), len(dec_), len({fam_of[l] for l in dec_}),
                      ", ".join(f"{l} ({first[l][1]})" for l in legs if first[l][1].startswith(str(y)) and first[l][1] != "1999-01")))
put_table("06f_legs_by_year", table(["year", "legs in January", "legs in December", "families in December", "legs starting that year"], yrows,
                                    "Legs active by year (years where the count changes; unchanged from the last row to 2021). Derived from table 06e."))
fact("legs_1999", yrows[0][1], "table 06f 1999 January")
for leg in ("IdioVol3F", "VolumeTrend", "TrendFactor", "ShareIss5Y"):
    y_, m_ = map(int, first[leg][1].split("-"))
    fact(f"start_{leg}", first[leg][1], f"table 06e first holding month of {leg}")
    fact(f"sig_{leg}", f"{y_ - (1 if m_ == 1 else 0)}-{(12 if m_ == 1 else m_ - 1):02d}", f"table 06e first signal month-end of {leg}")
fact("gate_ShareIss5Y", REG["ShareIss5Y"]["history_gate_months"], "registry ShareIss5Y history_gate_months")

# rf correction already in facts; skip1 (runs 050, 051, old bytes)
b050 = block("050")
b051 = block("051")
sk = [("ic_mean", 4), ("ic_tstat_nw", 2), ("ic_half1_mean", 4), ("ic_half2_mean", 4), ("ls_sharpe", 3), ("ls_ann_return_pct", 2),
      ("ls_raw_sharpe", 3), ("ls_sharpe_ex_top_years", 3)]
put_table("06g_skip1", table(["field", "run 050 (signal-close base)", "run 051 (skip1 base)"],
                             [(k, fnum(b050[k], nd), fnum(b051[k], nd)) for k, nd in sk] +
                             [("paired composite dIC (NW t)", "", f"{fsig(b051['paired_dic_mean'], 4)} ({fnum(b051['paired_dic_tstat_nw'], 2)})")],
                             "Return-start sensitivity, diagnostic only. Source: result blocks of runs 050 and 051 (HARNESS aef490297071, DATA 198b281de1a0: "
                             "pre-refresh bytes); finding_confirmed skip1_return_start_sensitivity."))
legkeys = sorted({k[len("legic_"):-len("_close")] for k in b051 if k.startswith("legic_") and k.endswith("_close")})
leg_col = {"f_size": "Size", "f_value": "Value", "f_prof": "Profitability", "f_inv": "Investment", "f_mom": "Momentum"}
rows = []
for lk in legkeys:
    rows.append((lk, fnum(b051[f"legic_{lk}_close"], 4), fnum(b051[f"legic_{lk}_close_t"], 2), fnum(b051[f"legic_{lk}_skip1"], 4),
                 fnum(b051[f"legic_{lk}_skip1_t"], 2), fsig(b051[f"legic_{lk}_delta"], 4), fnum(b051[f"legic_{lk}_delta_t"], 2)))
rows.sort(key=lambda r: float(r[6]))
put_table("06h_skip1_legs", table(["leg column", "IC close", "t", "IC skip1", "t", "delta", "delta t"], rows,
                                  "Per-leg standalone IC (within-sector rank, published sign), signal-close vs skip1 base, sorted by delta t. "
                                  "Source: run 051 `legic_*` fields (pre-refresh bytes)."))
fact("skip1_ic", fnum(b051["ic_mean"], 4), "run 051 ic_mean")
fact("skip1_close_ic", fnum(b050["ic_mean"], 4), "run 050 ic_mean")
fact("skip1_dic", fsig(b051["paired_dic_mean"], 4), "run 051 paired_dic_mean")
fact("skip1_dic_t", fnum(b051["paired_dic_tstat_nw"], 2), "run 051 paired_dic_tstat_nw")
fact("skip1_sh", fnum(b051["ls_sharpe"], 3), "run 051 ls_sharpe")
fact("close_sh", fnum(b050["ls_sharpe"], 3), "run 050 ls_sharpe")
fact("skip1_h2", fnum(b051["ic_half2_mean"], 4), "run 051 ic_half2_mean")
fact("close_h2", fnum(b050["ic_half2_mean"], 4), "run 050 ic_half2_mean")
fact("skip1_share", fnum(100 * -float(b051["paired_dic_mean"]) / float(b050["ic_mean"]), 0), "100 x -run 051 paired_dic_mean / run 050 ic_mean")
for lk, nm in leg_col.items():
    fact(f"seed_ic_{nm}", fnum(b051[f"legic_{lk}_close"], 4), f"run 051 legic_{lk}_close")
    fact(f"seed_t_{nm}", fnum(b051[f"legic_{lk}_close_t"], 2), f"run 051 legic_{lk}_close_t")

# Stage 3 (acceptance-time, run 043; run 048 reproduced it)
C = VER["v14"]["construction"]
cols = C["columns"]
s3rows = [(var,) + tuple(C[var]) for var in CFG["construction"]["variants"]]
put_table("06i_stage3", table(["variant"] + cols, s3rows,
                              "Stage 3 on v14, in-window, acceptance-time, pre-refresh bytes. Source: MODEL_MANIFEST.yaml v14 `construction` (run 043); run 048 "
                              "reproduced run 043 on every field but harness_sha (docs/JOURNAL.md, Phase E). Gross, hedged; raw Sharpe and full-window beta beside."))

# ============================================================================= Section 7: the construction layer

AUM = ("100", "1000", "5000")
VARS = ["layer", "layer_eta_0.25", "layer_eta_1", "layer_fixed_tier_spread", "layer_exec_half_month", "layer_tiered_borrow",
        "layer_no_buffer", "layer_no_beta_constraint", "layer_dollar_neutral_only", "equal_rank_decile", "buffered"]
lrows = []
for a in AUM:
    for var in VARS:
        b = L049[f"{var}@{a}M"]
        lrows.append((f"${a}M", var, fnum(b["gross_ann_return_pct"], 2), fnum(b["gross_sharpe"], 3), fnum(b["cost_spread_ann_pct"], 2),
                      fnum(b["cost_impact_ann_pct"], 2), fnum(b["cost_borrow_ann_pct"], 2), fnum(b["cost_total_ann_pct"], 2),
                      fnum(b["net_ann_return_pct"], 2), fnum(b["net_sharpe"], 3), fnum(b["net_tstat_nw"], 2), fnum(b["turnover_oneway_pct"], 1),
                      fnum(b["net_beta_on_market"], 3)))
put_table("07_layer049", table(["AUM", "variant", "gross ann %", "gross Sharpe", "spread", "impact", "borrow", "total cost", "net ann %", "net Sharpe",
                                "net NW t", "one-way turnover %", "net beta on M"], lrows,
                               "Construction layer on v14, in-window book 2001-01..2021-12 (252 months), pre-refresh bytes. Source: run 049 result blocks "
                               "(HARNESS 3561590b660a, LAYER 4b279fc317cd). Costs in %/yr; equal_rank_decile and buffered are the Stage 3 books unhedged under the same cost model."))
l = L049["layer@100M"]
fact("l49_gross", fnum(l["gross_ann_return_pct"], 2), "run 049 layer@100M gross_ann_return_pct")
fact("l49_gross_t", fnum(l["gross_tstat_nw"], 2), "run 049 layer@100M gross_tstat_nw")
fact("l49_cost", fnum(l["cost_total_ann_pct"], 2), "run 049 layer@100M cost_total_ann_pct")
fact("l49_spread", fnum(l["cost_spread_ann_pct"], 2), "run 049 layer@100M cost_spread_ann_pct")
fact("l49_impact", fnum(l["cost_impact_ann_pct"], 2), "run 049 layer@100M cost_impact_ann_pct")
fact("l49_borrow", fnum(l["cost_borrow_ann_pct"], 2), "run 049 layer@100M cost_borrow_ann_pct")
fact("l49_net", fnum(l["net_ann_return_pct"], 2), "run 049 layer@100M net_ann_return_pct")
fact("l49_net_sh", fnum(l["net_sharpe"], 3), "run 049 layer@100M net_sharpe")
fact("l49_to", fnum(l["turnover_oneway_pct"], 1), "run 049 layer@100M turnover_oneway_pct")
fact("l49_beta", fnum(l["net_beta_on_market"], 3), "run 049 layer@100M net_beta_on_market")
fact("l49_bias", fnum(l["bias_stat_mean"], 2), "run 049 layer@100M bias_stat_mean")
fact("l49_bias_band", fnum(l["bias_stat_in_band_pct"], 1), "run 049 layer@100M bias_stat_in_band_pct")
fact("l49_exante_vol", fnum(l["exante_vol_ann_pct_mean"], 2), "run 049 layer@100M exante_vol_ann_pct_mean")
fact("l49_real_vol", fnum(l["realised_vol_ann_pct_live"], 2), "run 049 layer@100M realised_vol_ann_pct_live")
fact("l57_bias_full", fnum(L057["layer@100M"]["bias_stat_mean"], 2), "run 057 layer@100M bias_stat_mean (1999-2026 book)")
fact("l49_net_1b", fnum(L049["layer@1000M"]["net_sharpe"], 3), "run 049 layer@1000M net_sharpe")
fact("l49_net_5b", fnum(L049["layer@5000M"]["net_sharpe"], 3), "run 049 layer@5000M net_sharpe")
fact("l49_fts_net_sh", fnum(L049["layer_fixed_tier_spread@100M"]["net_sharpe"], 3), "run 049 layer_fixed_tier_spread@100M net_sharpe")
fact("l49_erd_gross", fnum(L049["equal_rank_decile@100M"]["gross_ann_return_pct"], 2), "run 049 equal_rank_decile@100M gross_ann_return_pct")
fact("l49_erd_to", fnum(L049["equal_rank_decile@100M"]["turnover_oneway_pct"], 1), "run 049 equal_rank_decile@100M turnover_oneway_pct")
fact("l49_erd_gross_sh", fnum(L049["equal_rank_decile@100M"]["gross_sharpe"], 3), "run 049 equal_rank_decile@100M gross_sharpe")
fact("l49_nbc_beta", fnum(L049["layer_no_beta_constraint@100M"]["net_beta_on_market"], 3), "run 049 layer_no_beta_constraint@100M net_beta_on_market")
fact("l49_nbc_gross", fnum(L049["layer_no_beta_constraint@100M"]["gross_ann_return_pct"], 2), "run 049 layer_no_beta_constraint@100M gross_ann_return_pct")
fact("l49_nbc_gross_sh", fnum(L049["layer_no_beta_constraint@100M"]["gross_sharpe"], 3), "run 049 layer_no_beta_constraint@100M gross_sharpe")
TR = VER["v14"]["construction_layer"]["trading"]
fact("half_spread_bp", fnum(TR["implied_half_spread_bp"], 1), "manifest v14 construction_layer.trading.implied_half_spread_bp")
fact("fixed_half_spread_bp", fnum(TR["fixed_tier_half_spread_bp"], 1), "manifest v14 construction_layer.trading.fixed_tier_half_spread_bp")
fact("spread_measured", fnum(l["spread_measured_pct"], 2), "run 049 layer@100M spread_measured_pct")

# gross-vs-cost identity
idrows = []
maxgap = 0.0
for var in VARS:
    b = L049[f"{var}@100M"]
    g, c, gs, ns = (float(b[k]) for k in ("gross_ann_return_pct", "cost_total_ann_pct", "gross_sharpe", "net_sharpe"))
    pred = gs * (1 - c / g)
    maxgap = max(maxgap, abs(pred - ns))
    idrows.append((var, fnum(gs, 3), fnum(c / g, 3), fnum(pred, 3), fnum(ns, 3), fsig(ns - pred, 3),
                   fnum(b["gross_ann_vol_pct"], 2), fnum(b["net_ann_vol_pct"], 2)))
put_table("07b_identity", table(["variant @ $100M", "gross Sharpe", "cost / gross", "gross Sharpe x (1 - cost/gross)", "net Sharpe", "difference",
                                 "gross vol %", "net vol %"], idrows,
                                "The gross-versus-cost identity: with net vol close to gross vol, net Sharpe = gross Sharpe x (1 - cost/gross). "
                                "Source: run 049 result blocks, computed here."))
fact("identity_maxgap", fnum(maxgap, 3), "max |difference| in table 07b")
iw57 = []
for a in AUM:
    b = L057[f"layer@{a}M"]
    b49 = L049[f"layer@{a}M"]
    iw57.append((f"${a}M", fnum(b49["gross_ann_return_pct"], 2), fnum(b["cut_inwindow_gross_ann_return_pct"], 2), fnum(b49["gross_sharpe"], 3),
                 fnum(b["cut_inwindow_gross_sharpe"], 3), fnum(b49["cost_total_ann_pct"], 2), fnum(b["cut_inwindow_cost_total_ann_pct"], 2),
                 fnum(b49["net_sharpe"], 3), fnum(b["cut_inwindow_net_sharpe"], 3)))
put_table("07c_layer_restated", table(["AUM", "gross ann % (049)", "gross ann % (057 in-window)", "gross Sharpe (049)", "gross Sharpe (057 in-window)",
                                       "cost (049)", "cost (057 in-window)", "net Sharpe (049)", "net Sharpe (057 in-window)"], iw57,
                                      "The layer's in-window book (2001-01..2021-12) on the frozen bytes (run 049, DATA 198b281de1a0) and on the spend "
                                      "snapshot (run 057 `cut_inwindow_*`, DATA 42587e08609a). Same layer config 4b279fc317cd."))
fact("l57iw_net_sh", fnum(L057["layer@100M"]["cut_inwindow_net_sharpe"], 3), "run 057 layer@100M cut_inwindow_net_sharpe")
fact("l57iw_gross", fnum(L057["layer@100M"]["cut_inwindow_gross_ann_return_pct"], 2), "run 057 layer@100M cut_inwindow_gross_ann_return_pct")

# D7 harness moves
d7 = []
for i, e in ev("harness_changed"):
    if e["old_sha"] in ("73a95d352942", "471f70782486"):
        d7.append((i, e["ts"], e["old_sha"], e["new_sha"], e.get("tests_passed") or e.get("pytest", ""), safe_text(e["reason"], i, 420)))
put_table("07d_d7_changes", table(["events line", "ts", "old HARNESS", "new HARNESS", "tests", "reason (record text)"], d7,
                                  "The D7 layer changes and the alpha-review fixes. Source: events `harness_changed` (text truncated at 420 characters)."))

# ============================================================================= Section 8: out of sample

_, hx = ev_one("decision", id="holdout_expectations_v14_spend_snapshot")
fact("hx_text", hx["decision"], "events decision holdout_expectations_v14_spend_snapshot (verbatim)")
fact("hx_ts", hx["ts"], "events decision holdout_expectations_v14_spend_snapshot ts")
first_ho_run = ev_one("run_started", seq="054")
fact("ho_first_ts", first_ho_run[1]["ts"], "events run_started 054 ts")
assert hx["ts"] < first_ho_run[1]["ts"]
VE = VER["v14"]["holdout"]["vs_expectation"]
put_table("08_vs_expectation", table(["metric", "in-window expectation (run 053 unless noted)", "holdout", "holdout source"],
                                     [(k, v[0], v[1], v[2]) for k, v in VE.items()],
                                     "The holdout against the expectations written before it. Source: MODEL_MANIFEST.yaml v14 `holdout.vs_expectation` "
                                     "(= events `holdout_spent` vs_expectation); expectations from decision holdout_expectations_v14_spend_snapshot."))
ho_ic = annual_pairs(summary_line("054", "annual IC:"))
ho_ic = [(y, v) for y, v in ho_ic if y >= 2022]
s056 = {b["variant"]: b for b in blocks("056")}
ann_h = dict(annual_pairs(s056["equal_rank_decile"]["annual_returns_pct"]))
lay = L057["layer@100M"]
ann_lg = dict(annual_pairs(lay["annual_gross_returns_pct"]))
ann_ln = dict(annual_pairs(lay["annual_net_returns_pct"]))
put_table("08b_holdout_years", table(["year", "composite IC (054)", "hedged D10-D1 % (056 equal_rank_decile)", "layer@$100M gross % (057)", "layer@$100M net % (057)"],
                                     [(y, fsig(v, 3), fsig(ann_h[y], 1), fsig(ann_lg[y], 1), fsig(ann_ln[y], 1)) for y, v in ho_ic],
                                     "The holdout by calendar year (2026 is January-September). Sources: research/results/054_*_summary.md `annual IC`; "
                                     "run 056 equal_rank_decile `annual_returns_pct`; run 057 layer@100M `annual_gross_returns_pct`, `annual_net_returns_pct`."))
fact("ho_2022_ic", fsig(dict(ho_ic)[2022], 3), "054 summary annual IC 2022")
fact("ho_2022_h", fsig(ann_h[2022], 1), "056 equal_rank_decile annual 2022")
fact("n_ho_years", len(ho_ic), "054 summary annual IC years >= 2022")
fact("n_ho_years_left", len(ho_ic) - CFG["diagnostics"]["ex_regime_top_years"], "holdout calendar years minus top_years_k")
fact("ho_ex3_h", fnum(b055["ls_sharpe_ex_top_years"], 2), "run 055 ls_sharpe_ex_top_years")
fact("ho_ex3_x", fnum(b054["cut_holdout_ls_excess_sharpe_ex_top_years"], 2), "run 054 cut_holdout_ls_excess_sharpe_ex_top_years")
fact("ho_top_years", b054["cut_holdout_ls_excess_top_years"], "run 054 cut_holdout_ls_excess_top_years")
fact("ho_ic_h1_055", fnum(b055["ic_half1_mean"], 4), "run 055 ic_half1_mean")
fact("ho_ic_h2_055", fnum(b055["ic_half2_mean"], 4), "run 055 ic_half2_mean")
fact("ho_rf_credit", fnum(b054["cut_holdout_ls_rf_credit_pp"], 2), "run 054 cut_holdout_ls_rf_credit_pp")
fact("ho_ex_sh", fnum(b054["cut_holdout_ls_excess_sharpe"], 2), "run 054 cut_holdout_ls_excess_sharpe")
fact("ho_ex_ret", fnum(b054["cut_holdout_ls_excess_ann_return_pct"], 2), "run 054 cut_holdout_ls_excess_ann_return_pct")
fact("ho055_sh", fnum(b055["ls_sharpe"], 3), "run 055 ls_sharpe")
fact("ho055_ret", fnum(b055["ls_ann_return_pct"], 2), "run 055 ls_ann_return_pct")
fact("ho055_ic", fnum(b055["ic_mean"], 4), "run 055 ic_mean")
fact("ho055_raw", fnum(b055["ls_raw_ann_return_pct"], 2), "run 055 ls_raw_ann_return_pct")
fact("ho055_hedged_m", b055["ls_hedged_months"], "run 055 ls_hedged_months")
fact("ho055_raw_mdd", fnum(b055["ls_raw_maxdd_pct"], 2), "run 055 ls_raw_maxdd_pct")
fact("full054_raw_mdd", fnum(b054["ls_raw_maxdd_pct"], 2), "run 054 ls_raw_maxdd_pct (1999-2026)")
fact("ho_d1", dec055[0], "run 055 decile_avg_ret_pct D1")
fact("ho_d2_d10_min", min(dec055[1:], key=float), "run 055 decile_avg_ret_pct min of D2..D10")
fact("ho_d2_d10_max", max(dec055[1:], key=float), "run 055 decile_avg_ret_pct max of D2..D10")
hoti = [(t, b055[f"tier_{t}_ic_mean"], b055[f"tier_{t}_ls_sharpe"]) for t in ("MEGA", "MID", "SMALL")]
put_table("08c_holdout_tiers", table(["tier", "IC", "raw LS Sharpe"], hoti,
                                     "Liquidity tiers in the holdout (diagnostic). Source: run 055 `tier_*` fields (run 054's holdout cut prints no tiers)."))
hb = [("ex-ante beta, mean over holdout months", "run 054 cut_holdout_ls_beta_mean", fnum(b054["cut_holdout_ls_beta_mean"], 3)),
      ("ex-ante beta, mean (beta = 0 in 2022)", "run 055 ls_beta_mean", fnum(b055["ls_beta_mean"], 3)),
      ("realised beta of the raw LS, holdout", "run 055 ls_beta_fullwindow", fnum(b055["ls_beta_fullwindow"], 3)),
      ("ex-ante beta, last month", "run 054 ls_beta_last", fnum(b054["ls_beta_last"], 3)),
      ("ex-ante beta, mean in-window", "run 053 ls_beta_mean", fnum(b053["ls_beta_mean"], 3)),
      ("realised beta of the raw LS, in-window", "run 053 ls_beta_fullwindow", fnum(b053["ls_beta_fullwindow"], 3)),
      ("layer@$100M net beta on M, holdout", "run 057 cut_holdout_net_beta_on_market", fnum(lay["cut_holdout_net_beta_on_market"], 3)),
      ("layer@$100M net beta on M, in-window", "run 057 cut_inwindow_net_beta_on_market", fnum(lay["cut_inwindow_net_beta_on_market"], 3))]
put_table("08d_beta", table(["quantity", "source field", "value"], hb, "The hedge beta against the realised beta. Sources as named per row."))
lh = []
for a in AUM:
    for var in ("layer", "layer_fixed_tier_spread", "layer_no_beta_constraint", "equal_rank_decile"):
        b = L057[f"{var}@{a}M"]
        lh.append((f"${a}M", var, fnum(b["cut_holdout_gross_ann_return_pct"], 2), fnum(b["cut_holdout_gross_sharpe"], 3),
                   fnum(b["cut_holdout_cost_total_ann_pct"], 2), fnum(b["cut_holdout_net_ann_return_pct"], 2), fnum(b["cut_holdout_net_sharpe"], 3),
                   fnum(b["cut_holdout_net_beta_on_market"], 3)))
put_table("08e_layer_holdout", table(["AUM", "variant", "gross ann %", "gross Sharpe", "total cost %", "net ann %", "net Sharpe", "net beta on M"], lh,
                                     "The construction layer in the holdout (57 months). Source: run 057 `cut_holdout_*` fields."))
fact("l57ho_cost", fnum(lay["cut_holdout_cost_total_ann_pct"], 2), "run 057 layer@100M cut_holdout_cost_total_ann_pct")
_, vw55 = ev_one("validation_warning", seq="055")
fact("floor_warn", vw55["warnings"][1], "events validation_warning seq 055 warnings[1]")

# Stage 3 in the holdout spend (run 056): full window and printed annual returns only
s3h = []
for var in CFG["construction"]["variants"]:
    bb = s056[var]
    an = dict(annual_pairs(bb["annual_returns_pct"]))
    s3h.append((var, fnum(bb["ls_sharpe"], 3), fnum(bb["ls_raw_sharpe"], 3), fnum(bb["ls_beta_fullwindow"], 2)) +
               tuple(fsig(an[y], 1) for y in range(2022, 2027)))
put_table("08f_stage3_holdout", table(["variant", "Sharpe 1999-2026", "raw Sharpe 1999-2026", "beta 1999-2026", "2022 %", "2023 %", "2024 %", "2025 %", "2026 % (Jan-Sep)"], s3h,
                                      "Stage 3 variants in the spend run. Run 056 printed no holdout cut (process_finding stage3_holdout_cuts_absent), so only the "
                                      "1999-2026 full-window statistics and the printed calendar-year hedged returns exist. Source: run 056 result blocks."))
# 054's in-window cut against run 053
eq = [k for k in b054 if k.startswith("cut_inwindow_") and k[len("cut_inwindow_"):] in b053]
same054 = [k for k in eq if b054[k] == b053[k[len("cut_inwindow_"):]]]
fact("cont_same", len(same054), "run 054 cut_inwindow_* fields equal to the run 053 field of the same name")
fact("cont_n", len(eq), "run 054 cut_inwindow_* fields with a same-named run 053 field")

# ============================================================================= Section 9: integrity

ar = []
for i, e in ev("alpha_review"):
    f = e.get("findings", {})
    counts = ", ".join(f"{k} {v if isinstance(v, int) else len(v)}" for k, v in f.items())
    verdict = e.get("verdict", "")
    ar.append((i, e["ts"], safe_text(e["target"], i, 120), counts, safe_text(verdict, i)))
put_table("09_alpha_reviews", table(["events line", "ts", "target", "findings by severity", "verdict"], ar,
                                    "Every alpha-reviewer audit. Source: events `alpha_review` (finding lists counted)."))
fact("n_alpha_reviews", len(ar), "events alpha_review")
_phA = ev_one("phase_completed", phase="A")[0]
fact("n_alpha_phaseA", sum(1 for i, e in ev("alpha_review") if i < _phA), "events alpha_review before phase_completed A")
n_crit = sum((e["findings"].get("critical") if isinstance(e["findings"].get("critical"), int) else len(e["findings"].get("critical", []))) for _, e in ev("alpha_review"))
fact("n_alpha_critical", n_crit, "sum of critical findings over events alpha_review")
pf = []
for i, e in ev("process_finding"):
    sid = e.get("subject") or e.get("id")
    body = e.get("note") or e.get("action") or e.get("finding") or ""
    pf.append((i, e["ts"][:10], mask_id(sid), safe_text(body, i, 200)))
put_table("09b_process_findings", table(["events line", "date", "subject / id", "note or action (record text)"], pf,
                                        "Every process_finding. Source: events `process_finding` (text truncated at 200 characters; ids with the other project's "
                                        "name have that word masked as `other-project`; text that refers to another project is omitted and pointed to by line)."))
fact("n_process_findings", len(pf), "events process_finding")
fc = []
for i, e in ev("finding_corrected"):
    sid = e.get("subject") or e.get("id") or e.get("target")
    body = e.get("note") or e.get("correction") or e.get("evidence") or e.get("corrected") or json.dumps(e.get("changes") or e.get("fixes"))
    fc.append((i, e["ts"][:10], mask_id(sid), safe_text(body, i, 200)))
put_table("09c_findings_corrected", table(["events line", "date", "subject / id", "correction (record text)"], fc,
                                          "Every finding_corrected (append-only corrections). Source: events `finding_corrected` (text truncated at 200 characters)."))
fact("n_finding_corrected", len(fc), "events finding_corrected")
vc = [(i, e["ts"][:10], e["subject"], safe_text(e.get("detail") or e.get("evidence") or e.get("result"), i, 200)) for i, e in ev("verification_completed")]
put_table("09d_verifications", table(["events line", "date", "subject", "detail (record text)"], vc,
                                     "Every verification_completed. Source: events `verification_completed` (text truncated at 200 characters)."))
fcf = [(i, e["ts"][:10], e["subject"], safe_text(e.get("detail") or e.get("evidence") or e.get("note"), i, 200)) for i, e in ev("finding_confirmed")]
put_table("09e_findings_confirmed", table(["events line", "date", "subject", "evidence (record text)"], fcf,
                                          "Every finding_confirmed. Source: events `finding_confirmed` (text truncated at 200 characters)."))
leak_ids = [mask_id(e.get("id") or e.get("subject")) for i, e in ev("process_finding") if BANNED.search(json.dumps(e))]
fact("n_leak_findings", len(leak_ids), "process_findings whose record text refers to another project")

# ============================================================================= Section 10: orchestration

rc = {e["seq"]: (i, e) for i, e in ev("run_completed")}
runrows = []
total_s = 0.0
phase_s = {}
for i, e in run_started:
    seq = e["seq"]
    done = rc.get(seq)
    rt = float(done[1]["runtime_seconds"]) if done else None
    if rt is not None:
        total_s += rt
    n = int(seq)
    ph = "0" if n <= 2 else "B" if n <= 11 else "D" if n <= 44 else "E (D7, D8)" if n <= 53 else "E (holdout)"
    if rt is not None:
        phase_s[ph] = phase_s.get(ph, 0.0) + rt
    fac = e["factors"] if isinstance(e["factors"], str) else ",".join(e["factors"])
    runrows.append((seq, e["label"], e["stage"], e["ts"], fnum(rt, 1) if rt is not None else "aborted", e["harness_sha"], e["config_sha"],
                    e["composite_sha"], e["data_sha"], fac if len(fac) < 60 else str(len(e["factors"])) + " factors"))
put_table("10_runs", table(["run", "label", "stage", "started (UTC)", "runtime s", "HARNESS", "CONFIG", "COMPOSITE", "DATA", "factors"], runrows,
                           "Every run. Source: events `run_started` and `run_completed` (runtime_seconds); run 046 has a `run_aborted` event and no runtime."))
fact("n_runs_completed", len(rc), "events run_completed")
fact("wall_hours", fnum(total_s / 3600.0, 1), "sum of run_completed runtime_seconds / 3600")
fact("wall_seconds", fnum(total_s, 1), "sum of run_completed runtime_seconds")
put_table("10b_runtime_by_phase", table(["phase", "runs completed", "runtime h"],
                                        [(ph, sum(1 for r in runrows if r[4] != "aborted" and (
                                            ("0" if int(r[0]) <= 2 else "B" if int(r[0]) <= 11 else "D" if int(r[0]) <= 44 else "E (D7, D8)" if int(r[0]) <= 53 else "E (holdout)") == ph)),
                                          fnum(s_ / 3600.0, 2)) for ph, s_ in phase_s.items()],
                                        "Run wall time by phase (runs 001-002 bootstrap, 003-011 Phase B, 012-044 Phase D, 045-053 Phase E and D8, 054-057 holdout). "
                                        "Source: events `run_completed` runtime_seconds."))
_, ab = ev_one("run_aborted")
fact("aborted_seq", ab["seq"], "events run_aborted seq")
sm = []
_, bs = ev_one("finding_corrected", subject="bootstrap_stamps")
sm.append((next(i for i, e in EV if e["event"] == "finding_corrected" and e.get("subject") == "bootstrap_stamps"), bs["ts"], "first commit " + bs["commit"], "HARNESS / CONFIG / COMPOSITE / DATA",
           f"{bs['harness_sha']} / {bs['config_sha']} / {bs['composite_sha']} / {bs['data_sha']}", "stamps of the first commit (finding_corrected bootstrap_stamps)"))
for i, e in EV:
    k = e["event"]
    if k in ("harness_changed", "config_changed"):
        if "see provenance" in str(e.get("new_sha")):
            continue
        sm.append((i, e["ts"], k, e["old_sha"], e["new_sha"], safe_text(e["reason"], i, 160)))
    elif k == "snapshot_recorded":
        sm.append((i, e["ts"], k, e.get("old_data_sha", "nodata"), e.get("data_sha") or e.get("new_data_sha"), safe_text(e.get("reason") or e.get("detail"), i, 160)))
    elif k == "composite_updated":
        sm.append((i, e["ts"], k + " " + e["model_version"], "", e["composite_sha"], "runs " + e["seq"]))
put_table("10c_stamp_moves", table(["events line", "ts (UTC)", "event", "old", "new", "reason (record text, truncated at 160)"], sm,
                                   "Every stamp move. Source: events `harness_changed`, `config_changed`, `snapshot_recorded`, `composite_updated`, and "
                                   "finding_corrected bootstrap_stamps for the first commit (the two bootstrap rows that preceded it carry no SHA)."))
fact("n_harness_moves", sum(1 for i, e in ev("harness_changed") if "see provenance" not in e["new_sha"]), "events harness_changed with a SHA")
fact("n_config_moves", sum(1 for i, e in ev("config_changed") if "see provenance" not in e["new_sha"]), "events config_changed with a SHA")
fact("n_snapshot_moves", len(ev("snapshot_recorded")), "events snapshot_recorded")
fact("n_composite_moves", len(ev("composite_updated")), "events composite_updated")
cnt = {}
for _, e in EV:
    cnt[e["event"]] = cnt.get(e["event"], 0) + 1
put_table("10d_event_counts", table(["event", "count"], sorted(cnt.items(), key=lambda x: (-x[1], x[0])),
                                    f"research/events.jsonl by event type ({len(EV)} rows)."))
fact("n_events", len(EV), "research/events.jsonl rows")
adv = []
for i, e in EV:
    if e.get("advisor") or (e["event"] == "decision" and "Advisor consulted" in e.get("decision", "")):
        adv.append((i, e["ts"], e.get("id", e["event"]), e.get("advisor") or "decision text: 'Advisor consulted'"))
put_table("10e_advisor", table(["events line", "ts", "decision", "record"], adv,
                               "Advisor consultations recorded in the event log. Source: events with an `advisor` field or 'Advisor consulted' in the decision text."))
fact("n_advisor", len(adv), "rows of table 10e")
ow = []
for i, e in EV:
    if "verbatim" in e:
        ow.append((i, e["ts"], e.get("id"), '"' + e["verbatim"] + '"', "verbatim"))
_, rcf = ev_one("rule_conflict_found")
ow.insert(0, (next(i for i, e in EV if e["event"] == "rule_conflict_found"), rcf["ts"], "rule_conflict_found " + rcf["subject"],
              rcf["resolved_by"], "paraphrase in the record"))
put_table("10f_owner", table(["events line", "ts", "record", "owner's input", "form"], ow,
                             "The owner's inputs as recorded. Source: events with a `verbatim` field, and rule_conflict_found (resolved_by)."))
_, deny = ev_one("process_finding", subject="v12_apply_permission_denied")
fact("deny_text", deny["evidence"], "events process_finding v12_apply_permission_denied evidence")
_tr = sorted({e["factor"] for i, e in ev("factor_translated")})
_tr_unscreened = [f for f in _tr if f not in REG]
fact("n_translated_distinct", len(_tr), "distinct factors over events factor_translated")
fact("translated_unscreened", ", ".join(_tr_unscreened), "factor_translated factors without a registry row (failed preflight; frontier)")
fact("n_spec_distinct", len({e["factor"] for i, e in ev("spec_written")}), "distinct factors over events spec_written")
fact("spent_on", MAN["holdout"]["spent_on"], "MODEL_MANIFEST.yaml holdout.spent_on")
for k in ("spec_written", "fields_verified", "factor_translated", "preflight_passed", "preflight_failed", "alpha_review", "factor_evaluated", "decision"):
    fact(f"cnt_{k}", cnt.get(k, 0), f"events {k} count")

jr = open(ROOT / "docs/JOURNAL.md").read()
m_ = re.search(r"session: (Opus [\d.]+) runner, (Fable [\d.]+) advisor", jr)
fact("model_runner", "Claude " + m_.group(1), "docs/JOURNAL.md 'snapshot recorded' entry")
fact("model_advisor", "Claude " + m_.group(2), "docs/JOURNAL.md 'snapshot recorded' entry")
m_ = re.search(r"session: (Fable [\d.]+), run from", jr)
fact("model_bootstrap", "Claude " + m_.group(1), "docs/JOURNAL.md bootstrap entry")
fact("journal_phaseB_h", re.search(r"Cost: ([\d.]+) h of screening", jr).group(1), "docs/JOURNAL.md Phase B entry")
fact("phaseB_h", fnum(phase_s["B"] / 3600.0, 2), "sum of run_completed runtime_seconds, runs 003-011 / 3600")
fact("phaseD_h", fnum(phase_s["D"] / 3600.0, 2), "sum of run_completed runtime_seconds, runs 012-044 / 3600")
fact("osap_tag", CFG["osap_source"]["tag"], "config osap_source.tag")

# ============================================================================= Appendices

rows = []
for n in sorted(IDX, key=lambda s: (s.lower(), s)):
    r = IDX[n]
    reg = REG.get(n, {})
    rows.append((n, r["status"], r.get("batch"), r.get("run"), reg.get("stage2_run") or "", r.get("family") or "",
                 r.get("ic"), r.get("ic_t"), r.get("raw_ret"), r.get("ret"), r.get("sharpe"), r.get("cov"), r.get("beta"), r.get("sh_exreg"),
                 r.get("resid_t") if r.get("resid_t") is not None else "", r.get("dls_t") if r.get("dls_t") is not None else "",
                 r.get("decided_by") or ""))
put_table("A1_registry", table(["name", "status", "batch", "Stage 1 run", "Stage 2 run", "family", "IC", "IC NW t", "raw LS %/yr", "hedged LS %/yr",
                                "hedged Sharpe", "coverage %", "beta", "Sharpe ex top-3", "resid t", "guard t", "decided by"], rows,
                               f"The full registry, {len(rows)} rows (five seed legs carry no screen). Source: research/registry_index.yaml (derived from "
                               "research/registry/*.yaml) and `stage2_run` from the rows. Acceptance-time, pre-refresh bytes."))
# gap check on Stage 2 rows
gaps = []
for n, r in IDX.items():
    if REG.get(n, {}).get("stage2_run"):
        for k in ("resid_t", "dls_t", "beta", "sh_exreg", "family", "decided_by"):
            if r.get(k) in (None, ""):
                gaps.append((n, k))
fact("n_index_gaps", len(gaps), "Stage 2 rows of registry_index missing resid_t/dls_t/beta/sh_exreg/family/decided_by")
fact("n_index_s2", sum(1 for n in IDX if REG.get(n, {}).get("stage2_run")), "registry_index rows with a stage2_run")

frows = [(k, FRONT[k]["class"], FRONT[k].get("date", ""), safe_text(FRONT[k]["reason"], 0)) for k in sorted(FRONT, key=lambda s: (s.lower(), s))]
put_table("A2_frontier", table(["OSAP acronym", "class", "date", "reason (record text)"], frows,
                               f"The frontier: every OSAP predictor not tested, {len(frows)} rows. Source: osap_source/osap_frontier.yaml `excluded`."))

# ============================================================================= write

TABLES.mkdir(exist_ok=True)
for old in glob.glob(str(TABLES / "*.md")):
    stem = Path(old).stem
    if stem != "00_facts" and stem not in TBL:
        Path(old).unlink()
for name in sorted(TBL):
    assert not BANNED.search(TBL[name]), name
    (TABLES / f"{name}.md").write_text(TBL[name])
facts_tbl = table(["key", "value", "source"], [(k, v, s) for k, (v, s) in sorted(FACTS.items())],
                  "Every scalar the prose uses, with its record source. Generated by paper/build_tables.py.")
(TABLES / "00_facts.md").write_text(facts_tbl)

src_path = PAPER / "paper_src.md"
if src_path.exists():
    src = src_path.read_text()

    def sub(m):
        key = m.group(1)
        if key == "table:00_facts":
            return facts_tbl.rstrip("\n")
        if key.startswith("table:"):
            return TBL[key[6:]].rstrip("\n")
        return FACTS[key][0]
    out = re.sub(r"\{\{([^}]+)\}\}", sub, src)
    (PAPER / "paper.md").write_text(out)
    if "--check" in sys.argv:
        bare = re.sub(r"\{\{[^}]+\}\}", "", src)
        bare = re.sub(r"`[^`]*`", "", bare)
        hand = re.findall(r"(?<![\w.\-])-?\d+\.\d+(?![\w.])", bare)
        bad = [h for h in hand]
        if bad:
            print("hand-typed decimals in paper_src.md:", sorted(set(bad)))
            sys.exit(1)
        hits = [l for l in out.splitlines() if BANNED.search(l)]
        if len(hits) > 1:
            print("words naming the other project on more than one line of paper.md:", hits)
            sys.exit(1)
        print("check OK:", len(TBL), "tables,", len(FACTS), "facts")
print("wrote", len(TBL), "tables and", len(FACTS), "facts")
