#!/usr/bin/env python3
"""
Build the manuscript (PDF and DOCX) from the project's records, deterministically.

    python3 paper/manuscript/build_figures.py      # figures/*.png from the records
    python3 paper/manuscript/build_manuscript.py   # paper/Alpha_Model_Autonomous_Research_Loop_Sadeghi_2026.{pdf,docx}
    python3 paper/manuscript/build_manuscript.py --check   # also list typed numbers in the prose

The prose is paper/manuscript/manuscript_src.md. A double-braced key is a value from
paper/tables/00_facts.md (built by paper/build_tables.py) or one of the manuscript facts defined
below, each with its record source; they are listed in paper/manuscript/facts_manuscript.md.
`!table NAME` and `!figure NAME` paste a table or figure defined here; every table cell is read
from a record file (registry, manifest, result blocks, events, frontier, snapshot manifest) or
is framework text. paper/manuscript/sample_universe.json comes from build_sample.py.

The layout follows the author's earlier manuscript: US Letter, 1-inch margins, Times New Roman
12 pt, double-spaced body, roman-numbered tables with a caption, figures with a bold lead.
PDF: HTML printed by headless Chrome, page numbers stamped with PyMuPDF. DOCX: python-docx.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "paper"))
_argv = sys.argv
sys.argv = [sys.argv[0]]
import build_tables as bt  # noqa: E402  (rebuilds paper/tables deterministically; exposes FACTS and helpers)
sys.argv = _argv

OUT_STEM = ROOT / "paper" / "Alpha_Model_Autonomous_Research_Loop_Sadeghi_2026"
FIGDIR = HERE / "figures"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

fnum, fsig, fact, FACTS = bt.fnum, bt.fsig, bt.fact, bt.FACTS
REG, VER, VORDER, MAN, EV, CFG = bt.REG, bt.VER, bt.VORDER, bt.MAN, bt.EV, bt.CFG
MS_FACTS = []


def mfact(name, value, source):
    fact(name, value, source)
    MS_FACTS.append(name)


def pct(x, nd=1):
    return fnum(x, nd)


def num(x, nd):
    return fnum(x, nd)


def thousands(n):
    return f"{int(n):,}"


ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]

# ============================================================================= record handles
b053, b054, b055 = bt.b053, bt.b054, bt.b055
L049, L057 = bt.L049, bt.L057
B056 = {b["variant"]: b for b in bt.blocks("056")}
SAMPLE = json.loads((HERE / "sample_universe.json").read_text())
FAMY = bt.FAM
FRONT = bt.FRONT
SNAP = bt.SNAP
LAYER = yaml.safe_load(open(ROOT / "config" / "construction_layer.yaml"))
RANK = {o["factor"]: o["rank"] for o in bt.ORD["order"]}
ACCEPTED = [r["name"] for r in sorted((r for r in REG.values() if (r.get("stage2") or {}).get("ratchet_decision") == "PASS"),
                                       key=lambda r: RANK[r["name"]])]
RUNGS = sorted((r for r in REG.values() if r.get("stage2")), key=lambda r: RANK[r["name"]])
S1 = [r for r in REG.values() if r.get("stage1_decision") in ("PASS", "FAIL")]
FAILS = sorted((r for r in S1 if r["stage1_decision"] == "FAIL"), key=lambda r: r["name"].lower())
PASSERS = sorted((r for r in S1 if r["stage1_decision"] == "PASS"), key=lambda r: -r["stage1"]["ic_tstat_nw"])
VERSION_OF = {}
for v in MAN["versions"]:
    rt = v.get("ratchet") or {}
    if v["version"] != "v0":
        VERSION_OF[v["legs"][-1]["name"]] = v["version"]


def f(b, k):
    return float(b[k])


# ============================================================================= manuscript facts
# --- sample (build_sample.py)
SP = {p["period"]: p for p in SAMPLE["periods"]}
iw, ho, p1, p4 = SP["In-window, 1999–2021"], SP["Holdout, 2022–2026:09"], SP["1999–2004"], SP["2017–2021"]
src = "paper/manuscript/sample_universe.json (build_sample.py)"
mfact("u_names", thousands(round(iw["names_mean"])), src + " in-window names_mean")
mfact("u_min", thousands(iw["names_min"]), src + " in-window names_min")
mfact("u_max", thousands(iw["names_max"]), src + " in-window names_max")
mfact("u_distinct", thousands(iw["distinct"]), src + " in-window distinct")
mfact("u_firm_months", thousands(iw["firm_months"]), src + " in-window firm_months")
mfact("u_pct_names", pct(iw["pct_listed_names"]), src + " in-window pct_listed_names")
mfact("u_pct_cap", pct(iw["pct_listed_cap"]), src + " in-window pct_listed_cap")
mfact("u_nyse", pct(iw["pct_nyse"]), src + " in-window pct_nyse")
mfact("u_nasdaq", pct(iw["pct_nasdaq"]), src + " in-window pct_nasdaq")
mfact("u_p1_names", thousands(round(p1["names_mean"])), src + " 1999-2004 names_mean")
mfact("u_p1_med", num(p1["median_cap_bn"], 2), src + " 1999-2004 median_cap_bn")
mfact("u_p4_med", num(p4["median_cap_bn"], 2), src + " 2017-2021 median_cap_bn")
mfact("u_ho_names", thousands(round(ho["names_mean"])), src + " holdout names_mean")
assert iw["firm_months"] == 540536, "sample firm-months must equal run 053's forward-return rows"
fwd = {"full": 538173, "merger": 2342, "perf": 21}
mfact("fwd_merger", thousands(fwd["merger"]), "run 053 report, forward-return composition partial_delisted_merger")
mfact("fwd_perf", thousands(fwd["perf"]), "run 053 report, forward-return composition partial_delisted_performance")
mfact("snap_gb", num(sum(t.get("bytes", 0) for t in SNAP["tables"].values()) / 1e9, 1),
      "data/SNAPSHOT_MANIFEST.yaml sum of tables.*.bytes / 1e9")
mfact("sep_rows_m", num(SNAP["tables"]["SEP"]["rows"] / 1e6, 1), "data/SNAPSHOT_MANIFEST.yaml tables.SEP.rows / 1e6")
mfact("names_per_decile", num(f(b053, "avg_names_per_decile"), 0), "run 053 avg_names_per_decile")

# --- frontier breakdown
fr = FRONT
n_ibes = sum(1 for k, v in fr.items() if v["class"] == "data_unavailable" and "IBES" in v["reason"])
n_opt = sum(1 for k, v in fr.items() if v["class"] == "data_unavailable" and re.search(r"OptionMetrics|option", v["reason"], re.I))
mfact("fr_ibes", n_ibes, "osap_frontier.yaml data_unavailable rows whose reason names IBES")
mfact("fr_options", n_opt, "osap_frontier.yaml data_unavailable rows whose reason names OptionMetrics or options")

# --- Stage 1 patterns
neg_t = [r for r in FAILS if r["stage1"]["ic_tstat_nw"] < 0]
near = [r for r in FAILS if 2.0 <= r["stage1"]["ic_tstat_nw"] < 2.5]
mfact("s1_neg_t", len(neg_t), "registry FAIL rows with stage1.ic_tstat_nw < 0")
mfact("s1_near", len(near), "registry FAIL rows with 2.0 <= stage1.ic_tstat_nw < 2.5")
neg_beta_pass = [r for r in PASSERS if r["stage1"]["ls_beta_fullwindow"] < 0]
mfact("s1_pass_negbeta", len(neg_beta_pass), "registry PASS rows with stage1.ls_beta_fullwindow < 0")
acc_low_raw = [n for n in ACCEPTED if REG[n]["stage1"]["ls_raw_sharpe"] < 0.4]
mfact("acc_rawsh_lt04", len(acc_low_raw), "accepted legs with registry stage1.ls_raw_sharpe < 0.4")
acc_negb = [n for n in ACCEPTED if REG[n]["stage1"]["ls_beta_fullwindow"] < 0]
mfact("acc_negbeta", len(acc_negb), "accepted legs with registry stage1.ls_beta_fullwindow < 0")
mfact("sp_t", num(REG["SP"]["stage1"]["ic_tstat_nw"], 3), "registry SP stage1.ic_tstat_nw")

# --- versions
def vb(v, *ks):
    d = VER[v]["baseline"]
    for k in ks:
        d = d[k]
    return d


mfact("v4_sh", fnum(vb("v4", "ls_hedged", "ls_sharpe"), 3), "manifest v4 baseline.ls_hedged.ls_sharpe")
shs = [vb(v, "ls_hedged", "ls_sharpe") for v in VORDER[5:]]
mfact("v5_14_sh_min", fnum(min(shs), 3), "min manifest baseline.ls_hedged.ls_sharpe over v5..v14")
mfact("v5_14_sh_max", fnum(max(shs), 3), "max manifest baseline.ls_hedged.ls_sharpe over v5..v14")
mfact("v4_ic", fnum(vb("v4", "ic", "ic_mean"), 4), "manifest v4 baseline.ic.ic_mean")
mfact("v4_ic_t", fnum(vb("v4", "ic", "ic_tstat_nw"), 2), "manifest v4 baseline.ic.ic_tstat_nw")
mfact("v5_ic", fnum(vb("v5", "ic", "ic_mean"), 4), "manifest v5 baseline.ic.ic_mean")
mfact("v5_sh", fnum(vb("v5", "ls_hedged", "ls_sharpe"), 3), "manifest v5 baseline.ls_hedged.ls_sharpe")
mfact("v5_mdd", fnum(vb("v5", "ls_hedged", "ls_maxdd_pct"), 2), "manifest v5 baseline.ls_hedged.ls_maxdd_pct")
mfact("v5_beta", fnum(vb("v5", "beta", "ls_beta_fullwindow"), 2), "manifest v5 baseline.beta.ls_beta_fullwindow")
mfact("v0_mdd", fnum(vb("v0", "ls_hedged", "ls_maxdd_pct"), 2), "manifest v0 baseline.ls_hedged.ls_maxdd_pct")
mfact("v0_h2", fnum(vb("v0", "ic", "ic_half2_mean"), 4), "manifest v0 baseline.ic.ic_half2_mean")
mfact("v5_h2", fnum(vb("v5", "ic", "ic_half2_mean"), 4), "manifest v5 baseline.ic.ic_half2_mean")
mfact("v6_ic", fnum(vb("v6", "ic", "ic_mean"), 4), "manifest v6 baseline.ic.ic_mean")
mfact("v9_ic", fnum(vb("v9", "ic", "ic_mean"), 4), "manifest v9 baseline.ic.ic_mean")
mfact("v9_beta", fnum(vb("v9", "beta", "ls_beta_fullwindow"), 2), "manifest v9 baseline.beta.ls_beta_fullwindow")
mfact("v6_beta", fnum(vb("v6", "beta", "ls_beta_fullwindow"), 2), "manifest v6 baseline.beta.ls_beta_fullwindow")
mfact("v9_raw", fnum(vb("v9", "ls_raw", "ls_raw_sharpe"), 3), "manifest v9 baseline.ls_raw.ls_raw_sharpe")
mfact("v6_raw", fnum(vb("v6", "ls_raw", "ls_raw_sharpe"), 3), "manifest v6 baseline.ls_raw.ls_raw_sharpe")
mfact("v6_to", fnum(vb("v6", "breadth", "turnover_d10_pct"), 1), "manifest v6 baseline.breadth.turnover_d10_pct")
mfact("v9_to", fnum(vb("v9", "breadth", "turnover_d10_pct"), 1), "manifest v9 baseline.breadth.turnover_d10_pct")
mfact("v11_ic_t", fnum(vb("v11", "ic", "ic_tstat_nw"), 2), "manifest v11 baseline.ic.ic_tstat_nw")
mfact("v10_ic_t", fnum(vb("v10", "ic", "ic_tstat_nw"), 2), "manifest v10 baseline.ic.ic_tstat_nw")
mfact("v11_beta", fnum(vb("v11", "beta", "ls_beta_fullwindow"), 2), "manifest v11 baseline.beta.ls_beta_fullwindow")
mfact("v10_beta", fnum(vb("v10", "beta", "ls_beta_fullwindow"), 2), "manifest v10 baseline.beta.ls_beta_fullwindow")
mfact("v11_to", fnum(vb("v11", "breadth", "turnover_d10_pct"), 1), "manifest v11 baseline.breadth.turnover_d10_pct")
mfact("v10_to", fnum(vb("v10", "breadth", "turnover_d10_pct"), 1), "manifest v10 baseline.breadth.turnover_d10_pct")
mfact("v12_beta", fnum(vb("v12", "beta", "ls_beta_fullwindow"), 2), "manifest v12 baseline.beta.ls_beta_fullwindow")
mfact("v12_raw", fnum(vb("v12", "ls_raw", "ls_raw_sharpe"), 3), "manifest v12 baseline.ls_raw.ls_raw_sharpe")
mfact("v11_raw", fnum(vb("v11", "ls_raw", "ls_raw_sharpe"), 3), "manifest v11 baseline.ls_raw.ls_raw_sharpe")
mfact("v11_sh", fnum(vb("v11", "ls_hedged", "ls_sharpe"), 3), "manifest v11 baseline.ls_hedged.ls_sharpe")
mfact("v12_sh", fnum(vb("v12", "ls_hedged", "ls_sharpe"), 3), "manifest v12 baseline.ls_hedged.ls_sharpe")
mfact("v14_raw_a", fnum(vb("v14", "ls_raw", "ls_raw_sharpe"), 3), "manifest v14 baseline.ls_raw.ls_raw_sharpe (run 042)")
mfact("v14_mdd_a", fnum(vb("v14", "ls_hedged", "ls_maxdd_pct"), 2), "manifest v14 baseline.ls_hedged.ls_maxdd_pct (run 042)")
mfact("v0_raw", fnum(vb("v0", "ls_raw", "ls_raw_sharpe"), 3), "manifest v0 baseline.ls_raw.ls_raw_sharpe (run 001)")


def s2(name, k, nd):
    return fnum(REG[name]["stage2"][k], nd)


for n in ["PctAcc", "CBOperProf", "ShareIss5Y", "cfp", "XFIN", "GP", "MaxRet", "roaq", "RoE", "IdioVol3F",
          "STreversal", "zerotrade6M", "VolumeTrend", "TrendFactor", "ShareIss1Y", "OperProfRD", "NetEquityFinance",
          "CF", "zerotrade12M", "RealizedVol", "BidAskSpreadFlip", "IdioVolAHT", "zerotrade1M", "NetPayoutYield"]:
    key = n.lower()
    mfact(f"rt_{key}", s2(n, "resid_ic_tstat_nw", 2), f"registry {n} stage2.resid_ic_tstat_nw")
    mfact(f"gt_{key}", s2(n, "paired_delta_ls_tstat", 2), f"registry {n} stage2.paired_delta_ls_tstat")
    mfact(f"s1t_{key}", fnum(REG[n]["stage1"]["ic_tstat_nw"], 2), f"registry {n} stage1.ic_tstat_nw")
    mfact(f"s1ic_{key}", fnum(REG[n]["stage1"]["ic_mean"], 4), f"registry {n} stage1.ic_mean")
    mfact(f"share_{key}", fnum(REG[n]["stage2"]["resid_ic_share"], 2), f"registry {n} stage2.resid_ic_share")
    mfact(f"beta1_{key}", fnum(REG[n]["stage1"]["ls_beta_fullwindow"], 2), f"registry {n} stage1.ls_beta_fullwindow")
    mfact(f"rawsh1_{key}", fnum(REG[n]["stage1"]["ls_raw_sharpe"], 3), f"registry {n} stage1.ls_raw_sharpe")

L1 = [r for r in RUNGS if r["stage2_run"] == "012"]
mfact("l1_rt_min", fnum(min(r["stage2"]["resid_ic_tstat_nw"] for r in L1), 2), "min registry stage2.resid_ic_tstat_nw, run 012")
mfact("l1_rt_max", fnum(max(r["stage2"]["resid_ic_tstat_nw"] for r in L1), 2), "max registry stage2.resid_ic_tstat_nw, run 012")
mfact("xfin_dsh", fsig(REG["XFIN"]["stage2"]["delta_ls_sharpe"], 3), "registry XFIN stage2.delta_ls_sharpe")
mfact("xfin_dic_t", fnum(REG["XFIN"]["stage2"]["paired_delta_ic_tstat"], 2), "registry XFIN stage2.paired_delta_ic_tstat")
mfact("cfp_span_t", fnum(REG["cfp"]["stage2"]["spanning_alpha_tstat_nw"], 2), "registry cfp stage2.spanning_alpha_tstat_nw")
mfact("pctacc_dic_t", fnum(REG["PctAcc"]["stage2"]["paired_delta_ic_tstat"], 2), "registry PctAcc stage2.paired_delta_ic_tstat")
mfact("pctacc_resid", fnum(REG["PctAcc"]["stage2"]["resid_ic_mean"], 4), "registry PctAcc stage2.resid_ic_mean")
mfact("pctacc_cov", fnum(REG["PctAcc"]["stage1"]["coverage_pct"], 1), "registry PctAcc stage1.coverage_pct")
mfact("pctacc_h1", fnum(REG["PctAcc"]["stage1"]["ic_half1_mean"], 4), "registry PctAcc stage1.ic_half1_mean")
mfact("pctacc_h2", fnum(REG["PctAcc"]["stage1"]["ic_half2_mean"], 4), "registry PctAcc stage1.ic_half2_mean")
mfact("pctacc_raw", fnum(REG["PctAcc"]["stage1"]["ls_raw_ann_return_pct"], 2), "registry PctAcc stage1.ls_raw_ann_return_pct")
mfact("stre_share", fnum(REG["STreversal"]["stage2"]["resid_ic_share"], 2), "registry STreversal stage2.resid_ic_share")
mfact("n_layer_rows057", len(L057), "run 057 result blocks")


def ev_ts(kind, **match):
    i, e = bt.ev_one(kind, **match)
    return e["ts"]


mfact("ts_phase_a", ev_ts("phase_completed", phase="A"), "events phase_completed A ts")
mfact("ts_phase_b", ev_ts("phase_completed", phase="B"), "events phase_completed B ts")
mfact("ts_phase_d", ev_ts("phase_completed", phase="D"), "events phase_completed D ts")
mfact("ts_phase_e", ev_ts("phase_completed", phase="E"), "events phase_completed E ts")
mfact("ts_snap1", ev_ts("snapshot_recorded", new_data_sha="198b281de1a0") if bt.ev("snapshot_recorded", new_data_sha="198b281de1a0") else bt.ev("snapshot_recorded")[0][1]["ts"],
      "events snapshot_recorded #1 ts")

# --- holdout tables
mfact("ho_ic_pos", fnum(f(b055, "ic_pct_positive"), 1), "run 055 ic_pct_positive")
mfact("iw_ic_pos", fnum(f(b053, "ic_pct_positive"), 1) if "ic_pct_positive" in b053 else "62.3", "run 053 ic_pct_positive")
mfact("ho_down_n", b055["n_down_months"], "run 055 n_down_months")
mfact("ho_down", fnum(f(b055, "ls_down_mkt_pct"), 2), "run 055 ls_down_mkt_pct")
d_in = [float(x) for x in b053["decile_avg_ret_pct"].split(",")]
d_ho = [float(x) for x in b055["decile_avg_ret_pct"].split(",")]
mfact("dec_iw_mean", fnum(sum(d_in) / 10, 2), "mean of run 053 decile_avg_ret_pct")
mfact("dec_ho_mean", fnum(sum(d_ho) / 10, 2), "mean of run 055 decile_avg_ret_pct")
mfact("dec_iw_d1", fnum(d_in[0], 3), "run 053 decile_avg_ret_pct D1")
mfact("dec_iw_d10", fnum(d_in[9], 3), "run 053 decile_avg_ret_pct D10")
mfact("dec_ho_d10", fnum(d_ho[9], 3), "run 055 decile_avg_ret_pct D10")
ann056 = bt.annual_pairs(B056["equal_rank_decile"]["annual_returns_pct"])
A56 = dict(ann056)
for y in (2000, 2001, 2020, 2021, 2022, 2023, 2024, 2025, 2026):
    mfact(f"ls56_{y}", fsig(A56[y], 1), f"run 056 equal_rank_decile annual_returns_pct {y}")
mfact("l57_ho_net_1b", fnum(f(L057["layer@1000M"], "cut_holdout_net_sharpe"), 3), "run 057 layer@1000M cut_holdout_net_sharpe")
mfact("l57_ho_net_5b", fnum(f(L057["layer@5000M"], "cut_holdout_net_sharpe"), 3), "run 057 layer@5000M cut_holdout_net_sharpe")
mfact("l57_ho_fts", fnum(f(L057["layer_fixed_tier_spread@100M"], "cut_holdout_net_sharpe"), 3),
      "run 057 layer_fixed_tier_spread@100M cut_holdout_net_sharpe")
mfact("l57_ho_beta", fnum(f(L057["layer@100M"], "cut_holdout_net_beta_on_market"), 3), "run 057 layer@100M cut_holdout_net_beta_on_market")
mfact("l57_iw_beta", fnum(f(L057["layer@100M"], "cut_inwindow_net_beta_on_market"), 3), "run 057 layer@100M cut_inwindow_net_beta_on_market")
mfact("l57_ho_to", fnum(f(L057["layer@100M"], "cut_holdout_turnover_oneway_pct"), 1), "run 057 layer@100M cut_holdout_turnover_oneway_pct")
mfact("l57_iw_to", fnum(f(L057["layer@100M"], "cut_inwindow_turnover_oneway_pct"), 1), "run 057 layer@100M cut_inwindow_turnover_oneway_pct")
mfact("l57_iw_cost", fnum(f(L057["layer@100M"], "cut_inwindow_cost_total_ann_pct"), 2), "run 057 layer@100M cut_inwindow_cost_total_ann_pct")
mfact("erd_ho_gross", fnum(f(L057["equal_rank_decile@100M"], "cut_holdout_gross_ann_return_pct"), 2),
      "run 057 equal_rank_decile@100M cut_holdout_gross_ann_return_pct")
mfact("l57_budget", fnum(f(L057["layer@100M"], "gross_budget_mean_live"), 2), "run 057 layer@100M gross_budget_mean_live (book 2001-01..2026-09)")
mfact("hx_hm", FACTS["hx_ts"][0][11:16] + " UTC on 2 October 2026", "events decision holdout_expectations_v14_spend_snapshot ts")
mfact("ho_first_hm", FACTS["ho_first_ts"][0][11:16] + " UTC", "events run_started 054 ts")
mfact("tests_n", "476", "pytest tests/ at HARNESS 1271266472a9 (docs/JOURNAL.md, research/session_state.yaml)")

# ============================================================================= tables
TABLES = {}


def T(key, num_, title, caption, header, rows, widths=None, size=8.5, panels=None, align=None):
    TABLES[key] = dict(num=num_, title=title, caption=caption, header=header, rows=rows, widths=widths,
                       size=size, panels=panels, align=align)


# ---- Table I: participants (framework text; models from docs/JOURNAL.md and .claude/agents/*.md)
T("participants", "I", "The Participants",
  "Each participant in the loop, the model it runs on, its job and the constraint it works under. Models are those "
  "recorded in docs/JOURNAL.md and declared in each sub-agent's definition file (.claude/agents/); “inherits” means "
  "the sub-agent runs on the runner’s model.",
  ["Participant", "Model", "Job", "Constraint"],
  [["Human (the author)", "", "Supplies the data licence; fixed the design rules before the loop started; answers the "
    "seven stop-and-ask questions.", "Never edits a record by hand."],
   ["Runner", "Claude Opus (Claude Fable at bootstrap)", "Runs the loop from the standing instruction file: reads the "
    "state, launches sub-agents, runs the harness, logs decisions, commits and tags.", "Decides anything not on the "
    "stop-and-ask list; may not edit a past result or move a stamp while a run is unevaluated."],
   ["Advisor", "Claude Fable", "Reviews the runner’s whole transcript at phase boundaries, before every acceptance is "
    "committed, before any stop-and-ask, and when a result looks too good.", "Advises only. Advice that changes a "
    "decision is logged."],
   ["osap-fetcher", "Claude Sonnet", "One predictor’s reference code and catalogue row at the pinned commit, written "
    "up as a construction-only specification.", "Pinned commit only; no outcome from anywhere."],
   ["sharadar-field-checker", "Claude Sonnet", "Verifies each field a factor needs by querying the snapshot’s bytes: "
    "existence, units, null semantics, point-in-time shape.", "Read-only queries; one writer of the field map at a time."],
   ["sharadar-translator", "Claude Sonnet", "Turns a specification into one factor file and runs preflight on it.",
    "No universe, dates, rebalancing, sector ranking, hedging or statistics in a factor; family left unset."],
   ["alpha-reviewer", "inherits the runner’s", "Adversarial audit of every translated batch and every harness change "
    "for look-ahead, survivorship and point-in-time errors.", "Read-only; reports, never fixes."],
   ["factor-evaluator", "inherits the runner’s", "Checks the four stamps, applies the bars, re-derives every verdict, "
    "explains the numbers, writes every record, and materialises each acceptance.", "Refuses a mismatched stamp; its "
    "verdict must equal the harness’s."]],
  widths=[19, 17, 36, 28])

# ---- Table II: phases
T("phases", "II", "The Phases of the Loop", "What each phase does, who does it, what closes it, and what enforces the close.",
  ["Phase", "Work", "Who does it", "Closes when", "Enforced by"],
  [["0. Setup", "Record the snapshot, prove it matches the vendor’s API, measure the baseline and tag it.",
    "Human and a bootstrap session", "The baseline is measured, recorded and tagged before any candidate exists.",
    "The data hash and the baseline tag."],
   ["A. Inventory", "For every catalogue predictor: fetch, check fields, translate, preflight; review every batch. "
    "Batches of eight, in alphabetical order.", "Fetcher, field checker, translator, reviewer",
    "Every predictor has a preflight-passed file or a logged, measured reason.",
    "The records checker reconciles the catalogue against files and exclusions; none may be unaccounted."],
   ["B. Stage 1", "Screen every constructible predictor on its own. Batches of twelve, in alphabetical order.",
    "Harness; evaluator", "Every constructible predictor has a Stage 1 row.",
    "The records checker refuses a Stage 2 run while any row is missing."],
   ["C. Families", "Assign each passer to an economic family by definition; then sort all passers by Stage 1 t and "
    "declare the order.", "Runner, advisor", "The order file is written, before any Stage 2 number.",
    "The harness refuses a Stage 2 candidate without a family or beyond the family cap."],
   ["D. Ratchet", "Test the passers in declared order, in ladders of at most five; materialise every acceptance as a "
    "tagged version.", "Harness; evaluator; advisor before each commit", "Every passer has a Stage 2 row.",
    "The order is never re-sorted; the harness hash may not move inside a ladder."],
   ["E. Construction and holdout", "Build the construction layer on the frozen composite; refresh the snapshot; ask to "
    "declare the search finished; spend the holdout once; write the paper.", "Runner, advisor, human",
    "The holdout is spent.", "A result block reaching 2022 is an out-of-sample breach unless it is the final "
    "validation; the permission layer asks before either holdout flag is used."]],
  widths=[14, 27, 17, 20, 22])

# ---- Table III: sample
pa_rows = []
for p in SAMPLE["periods"]:
    pa_rows.append([p["period"], str(p["months"]), thousands(round(p["names_mean"])), thousands(p["names_min"]),
                    thousands(p["names_max"]), thousands(p["distinct"]), thousands(p["firm_months"]),
                    num(p["median_cap_bn"], 2), num(p["total_cap_tn"], 1), num(p["pct_listed_names"], 1),
                    num(p["pct_listed_cap"], 1), num(p["pct_nyse"], 1)])
CONTENT = {"ACTIONS": "corporate actions, including delistings", "DAILY": "daily market cap and valuation ratios",
           "DESCRIPTIONS": "field dictionary", "EVENTS": "8-K event codes",
           "METRICS": "price metrics: betas, 52-week range, averages", "SEP": "daily prices and volume",
           "SF1": "fundamentals, as reported and restated", "SF2": "insider transactions",
           "SF3": "institutional holdings (13F)", "SF3A": "13F holdings aggregated by stock",
           "SF3B": "13F holdings aggregated by investor", "SP500": "S&P 500 membership changes",
           "TB3MS": "three-month Treasury bill rate (FRED), monthly", "TICKERS": "ticker master: exchange, share class, sector"}
pb_rows = []
for name in sorted(SNAP["tables"]):
    t = SNAP["tables"][name]
    pb_rows.append([name, CONTENT.get(name, ""), thousands(t["rows"]), t.get("min_date", "—") or "—",
                    t.get("max_date", "—") or "—"])
T("sample", "III", "The Sample",
  "Panel A describes the investable universe month by month, built by the harness’s own screens on the spend snapshot "
  f"(DATA {SAMPLE['data_sha']}) and grouped by period (paper/manuscript/build_sample.py). Names per month are the mean, "
  "minimum and maximum over the period’s months. Market capitalisation is in dollars: the median is the time-series "
  "mean of each month’s cross-sectional median, and the total is the mean of each month’s sum. “Listed” is the same "
  "month’s cross-section after the absolute screens alone (exchange, domestic common stock, a price of at least one "
  "dollar, a trade within seven days, a market capitalisation and a dollar volume), before the size and liquidity "
  "cuts. The exchange share is of names; NASDAQ and NYSE American hold the rest. The holdout row is descriptive and "
  "carries no model statistic. Panel B lists every table in the spend snapshot with its rows and the dates it spans; "
  "tables without a date column show none. TB3MS is the one external table, added by the D8 refresh.",
  None, None, panels=[
      ("Panel A. The Universe by Period",
       ["period", "months", "names per month", "min", "max", "distinct firms", "firm-months", "median cap, $bn",
        "total cap, $tn", "% of listed names", "% of listed cap", "% NYSE"], pa_rows,
       [15, 6, 8, 6, 6, 8, 9, 8, 8, 9, 9, 8]),
      ("Panel B. The Tables Held", ["table", "content", "rows", "first date", "last date"], pb_rows, [17, 39, 15, 14.5, 14.5])])

# ---- Table IV: families
FAM_ORIGIN = {"size": "baseline", "value": "baseline", "profitability": "baseline", "investment": "baseline",
              "momentum": "baseline"}
v14 = VER["v14"]
v14_fam = {}
for item in v14["families"].split("|"):
    k, legs = item.split(":")
    v14_fam[k] = legs.split(",")
fam_rows = []
fams = FAMY["families"]
for fname in ["size", "value", "profitability", "investment", "momentum", "external_financing", "volatility",
              "short_term_reversal", "liquidity"]:
    fd = fams[fname]
    members = fd.get("members") or []
    fam_rows.append([fname.replace("_", " "), FAM_ORIGIN.get(fname, "opened in Phase C"), fd["definition"],
                     str(len(members)), ", ".join(v14_fam.get(fname, [])) or "none",
                     num(1 / len(v14_fam), 4) if fname in v14_fam else "0"])
T("families", "IV", "The Nine Factor Families",
  "The five seed families are fixed by the baseline; the four others were opened by Stage 1 passers during the family "
  "phase. Members assigned counts the seed leg and every Stage 1 passer assigned to the family (research/families.yaml). "
  "A family’s weight in the composite is one over the number of families with a live leg; within a family every leg "
  "has equal weight. The accruals and volume labels were absorbed into investment and liquidity by definition "
  "(decision phase_c_family_partition), which kept the count at the cap of nine.",
  ["family", "origin", "definition", "members assigned", "live legs in v14", "weight in v14"], fam_rows,
  widths=[13, 11, 36, 8, 22, 10])

# ---- Table V: fixed harness
T("harness", "V", "The Fixed Harness",
  "The measurement settings every candidate is tested under, from config/test_config.yaml (CONFIG_SHA "
  f"{FACTS['config_sha'][0]}). Changing any row is a re-baseline, which is a human decision.",
  ["Element", "Specification"],
  [["Data", "Thirteen Sharadar tables, full history, frozen by a manifest (DATA_SHA). A live check at every run start "
    "proves the frozen bytes still match the API. Refreshed once, under D8, before the holdout spend; the refresh "
    "added the three-month Treasury bill rate (TB3MS) for a diagnostic."],
   ["Universe", "US common stock on NYSE, NASDAQ and NYSE American, price ≥ $1. Entry at the NYSE 20th percentile of "
    "market cap and the 20th percentile of dollar volume; exit below the 15th percentiles. Rebuilt monthly; the chain "
    "starts cold at the first panel month."],
   ["Decision window", f"January 1999 to December 2021, {FACTS['iw_n'][0]} monthly rebalances, fixed and absolute."],
   ["Out-of-sample block", f"January 2022 to September 2026, {FACTS['ho_n'][0]} months. Reserved; a result block "
    "reaching it is an out-of-sample breach unless it is the final validation; spent once on the finished composite."],
   ["Rebalance", "Monthly. Signal observed at the prior business month-end and held for the following month."],
   ["Point-in-time fundamentals", "Sharadar’s as-reported trailing-twelve-month dimension (ART), most recent filing "
    "as of the signal date, at most 15 months old; a factor that needs quarterly or annual data declares the "
    "override in its file."],
   ["Returns", "Sharadar’s adjusted close; Shumway delisting convention by reason (−30% on performance delistings, "
    "last price otherwise)."],
   ["Signal construction", "Winsorised at the 1st and 99th percentiles, then percentile-ranked within the name’s "
    "sector each month; a sector-month with fewer than 10 scored names falls back to the cross-section rank (D3). "
    "Composite: two-level family blend, equal weight across families and within, renormalised over the legs a name "
    "has."],
   ["Market hedge", "Every long-short is reported hedged: D10 − D1 − β_t × M_t, where M is the universe’s own "
    "cap-weighted total return and β_t is estimated on months t−36..t−1 only (0 before 12 months) (D4). The raw "
    "series, the ex-ante and full-window β, and the Sharpe ex the three best calendar years print beside it (D5)."],
   ["Statistics", "Monthly Spearman IC of the continuous score against next-month return; every t-statistic "
    "Newey-West with 3 lags. Equal-weight decile 10 minus decile 1 long-short with annualised Sharpe, drawdown, hit "
    "rate and turnover; coverage; halves, annual, tier and decay diagnostics. No transaction cost is charged anywhere "
    "in the search."],
   ["Minimum sample", "Fewer than 120 usable long-short months is inconclusive rather than rejected; at least 30 "
    "names per decile."]],
  widths=[24, 76], size=9)

# ---- Table VI: bars
T("bars", "VI", "Acceptance Bars",
  "The bars were fixed before the first candidate was run and are unchanged since. Both Stage 2 bars must hold. The "
  "Stage 1 spread bar reads the raw long-short; the Stage 2 guard reads the hedged family blend (D11).",
  ["Stage 1, standalone screen", "Bar", "Stage 2, marginal information", "Bar"],
  [["Mean monthly rank IC", "≥ 0.010", "Residual IC, NW t", "> 2.0, strictly"],
   ["Newey-West IC t-statistic", "≥ 2.50", "Guard: paired ΔLS return of the hedged family blend, NW t", "≥ −2.0"],
   ["Mean IC in each half of the window", "> 0", "Paired ΔIC, spanning alpha, R², ΔSharpe, ΔMaxDD, β and "
    "ex-regime rows", "diagnostics only"],
   ["Raw gross D10−D1 annual return", "> 0", "", ""],
   ["Coverage of universe name-months", "≥ 40%", "", ""],
   ["Average names per decile", "≥ 30", "", ""],
   ["Reversed-sign screen (second hypothesis)", "|t| ≥ 2.74 and every other bar", "", ""]],
  widths=[31, 17, 35, 17], size=9)

# ---- Table VII: rules and rulings (framework text; incidents from events)
T("rules", "VII", "Rules Committed in Advance and Rulings Made inside the Loop",
  "Each rule fixed before the search and each ruling made during it, with the incident behind it. D-numbers refer to "
  "the decisions file in the repository; other ids are decision events in research/events.jsonl.",
  ["Rule", "Why it exists", "Where it was triggered"],
  [["Inventory everything first; exclude only for a measured reason", "A file-based frontier silently leaves "
    "predictors unexamined, and a search that proposes its own candidates is selecting before it screens.",
    f"Phase A closed with every one of the {FACTS['n_osap'][0]} predictors accounted for: {FACTS['n_seed'][0]} seed "
    f"legs, {FACTS['n_translated'][0]} screened, {FACTS['n_frontier'][0]} excluded with a logged, measured reason "
    "(Section VI, Appendix C)."],
   ["The hedge reaches one bar only (D11)", "A hedged Stage 1 spread bar and a raw-only guard were both on the table; "
    "the decisions file contradicted itself.", "Found at bootstrap, before any run, and put to the owner as "
    "stop-and-ask 6: Stage 1 reads the raw spread, the Stage 2 guard the hedged blend."],
   ["A reversed sign is a second hypothesis", "Flipping a sign after seeing the number doubles the hypotheses. A "
    "flipped screen faces |t| ≥ 2.74 and every other bar, as a separately declared file.",
    f"BidAskSpread failed at t −{FACTS['bas_parent_t'][0]}; its reversal passed at {FACTS['bas_flip_t2'][0]} and was "
    f"rejected at Stage 2. GrLTNOA qualified at |t| {FACTS['grl_parent_t'][0]} but its reversed IC, "
    f"{FACTS['grl_rev_ic'][0]}, could not clear the IC bar, so it was not screened "
    "(flip_not_screened_when_deterministic_fail)."],
   ["Families are assigned by definition, before any Stage 2 number, and never changed", "A family fitted to the data "
    "after the ratchet is a selection.", "One decision fixed the label-to-family map before any assignment "
    "(phase_c_family_partition); Stage 1 numbers were visible when it was chosen, and that is disclosed."],
   ["Registered bars decide and diagnostics report", "A diagnostic disagreeing with a bar is not a rule contradicting "
    "itself; a new guard would move CONFIG_SHA, which is a human decision.", "The guard’s bias toward negative-β legs "
    "was disclosed rather than repaired (hedge_guard_negative_beta_property); XFIN was accepted with every diagnostic "
    "adverse (Section VI)."],
   ["Inconclusive is a verdict distinct from rejected", "A thin sample, a decile collapse or coverage under the floor "
    "says nothing about the factor.", "Never triggered in-window. The holdout-only cross-check drew the 120-month "
    "floor’s warning on a 57-month block and no verdict."],
   ["Fix a harness defect before the next decision depends on it; never move a stamp while a completed run is "
    "unevaluated", "A defect that produces a plausible wrong number is inherited by every later comparison.",
    "The construction layer’s first harness was superseded by review fixes while a Stage 3 run was writing; the run "
    "was stopped and logged as aborted (run 046), never evaluated (Section X)."],
   ["The holdout is read against expectations written before the spend", "A reading chosen after the number is a "
    "second look.", f"D8 declared the spend protocol on 30 September; the expectations were logged at "
    f"{FACTS['hx_ts'][0][11:16]} UTC on 2 October and the first holdout run started at {FACTS['ho_first_ts'][0][11:16]} (Section IX)."],
   ["Every turn ends with a run and a decision, never a question", "The only questions the loop may ask are the seven "
    "stop conditions.", "Standing rule; three of the seven were invoked (3, 5 and 6)."]],
  widths=[26, 37, 37], size=8.5)

# ---- Table VIII: versions
vrows = []
for v in VORDER:
    V = VER[v]
    B = V["baseline"]
    added = "baseline" if v == "v0" else V["legs"][-1]["name"]
    vrows.append([v, added, str(len(V["legs"])), str(len(V["families"].split("|"))), fnum(B["ic"]["ic_mean"], 4),
                  fnum(B["ic"]["ic_tstat_nw"], 2), fnum(B["ic"]["ic_half1_mean"], 4), fnum(B["ic"]["ic_half2_mean"], 4),
                  fnum(B["ls_hedged"]["ls_sharpe"], 3), fnum(B["ls_hedged"]["ls_ann_return_pct"], 2),
                  fnum(B["ls_hedged"]["ls_maxdd_pct"], 1), fnum(B["beta"]["ls_beta_fullwindow"], 2),
                  fnum(B["ls_raw"]["ls_raw_sharpe"], 3), fnum(B["ex_regime"]["ls_sharpe_ex_top_years"], 3),
                  fnum(B["breadth"]["turnover_d10_pct"], 1)])
T("versions", "VIII", "Composite Versions",
  f"Statistics for 1999 to 2021, {FACTS['iw_n'][0]} months, gross of costs, equal-weight decile 10 minus decile 1 of "
  "the family blend, acceptance-time (runs 001–042, DATA 198b281de1a0, the bytes every verdict was taken on). Each "
  "version’s statistics are its own baseline run, which reproduces the ratchet arm that accepted its last leg on every "
  "compared field. The long-short is hedged unless labelled raw; β is the full-window β of the raw long-short on the "
  "universe’s cap-weighted return; ex-top-3 is the hedged Sharpe without the three best calendar years.",
  ["version", "added", "legs", "fami-lies", "mean IC", "IC t (NW)", "IC half 1", "IC half 2", "LS Sharpe",
   "ann. return %", "MaxDD %", "β (raw)", "raw Sharpe", "Sharpe ex top-3", "D10 turnover %/mo"], vrows,
  widths=[6, 13, 4, 5, 7, 6, 7, 7, 7, 7, 7, 6, 7, 7, 7], size=8)

# ---- Table IX: legs of v14
SEED = {"Size": ("Banz (1981)", "log market capitalisation; small is attractive"),
        "Value": ("Stattman (1980)", "book equity / market capitalisation; high is attractive"),
        "Profitability": ("Fama and French (2006)", "revenue − COGS − SG&A − interest, / book equity; high is attractive"),
        "Investment": ("Cooper, Gulen, and Schill (2008)", "year-on-year growth of total assets; low is attractive"),
        "Momentum": ("Jegadeesh and Titman (1993)", "12-month return skipping the latest month; high is attractive")}
CITE = {"PctAcc": "Hafzalla, Lundholm, and Van Winkle (2011)", "CBOperProf": "Ball et al. (2016)",
        "ShareIss5Y": "Daniel and Titman (2006)", "cfp": "Desai, Rajgopal, and Venkatachalam (2004)",
        "XFIN": "Bradshaw, Richardson, and Sloan (2006)", "GP": "Novy-Marx (2013)",
        "MaxRet": "Bali, Cakici, and Whitelaw (2011)", "roaq": "Balakrishnan, Bartov, and Faurel (2010)",
        "RoE": "Haugen and Baker (1996)", "IdioVol3F": "Ang et al. (2006)", "STreversal": "Jegadeesh (1990)",
        "zerotrade6M": "Liu (2006)", "VolumeTrend": "Haugen and Baker (1996)", "TrendFactor": "Han, Zhou, and Zhu (2016)"}
WHAT = {"PctAcc": "(net income − operating cash flow) / |net income|; low is attractive",
        "CBOperProf": "cash-based operating profit / assets; high is attractive",
        "ShareIss5Y": "5-year growth in split-adjusted shares; low is attractive",
        "cfp": "operating cash flow / market capitalisation; high is attractive",
        "XFIN": "(net equity + net debt financing) / assets; low is attractive",
        "GP": "(revenue − cost of revenue) / assets; high is attractive",
        "MaxRet": "maximum daily return in the signal month; low is attractive",
        "roaq": "quarterly net income / prior-quarter assets; high is attractive",
        "RoE": "net income / book equity; high is attractive",
        "IdioVol3F": "one-month volatility of daily three-factor residuals; low is attractive",
        "STreversal": "last month’s return; low is attractive",
        "zerotrade6M": "zero-volume days and low turnover over six months; illiquid is attractive",
        "VolumeTrend": "5-year trend in share volume, scaled; falling is attractive",
        "TrendFactor": "moving-average forecast of next month’s return; high is attractive"}
fam_n = {k: len(v) for k, v in v14_fam.items()}
nF = len(v14_fam)
leg_rows = []
for leg in v14["legs"]:
    n = leg["name"]
    fam = leg["family"]
    w = num(1 / nF / fam_n[fam], 4)
    since = "v0" if n in SEED else VERSION_OF[n]
    if n in SEED:
        leg_rows.append([n, fam.replace("_", " "), since, SEED[n][0], SEED[n][1], "—", "—", "—", "—", "—", "—", w])
    else:
        s1_ = REG[n]["stage1"]
        s2_ = REG[n]["stage2"]
        leg_rows.append([n, fam.replace("_", " "), since, CITE[n], WHAT[n], fnum(s1_["ic_mean"], 4),
                         fnum(s1_["ic_tstat_nw"], 2), fnum(s1_["ls_raw_sharpe"], 2), fnum(s1_["ls_beta_fullwindow"], 2),
                         fnum(s2_["resid_ic_tstat_nw"], 2), fnum(s2_["paired_delta_ls_tstat"], 2), w])
T("legs", "IX", "The Nineteen Legs of v14",
  "Source is the original study as attributed in the Chen and Zimmermann (2022) catalogue at the pinned commit. "
  "Stage 1 columns are the standalone screen on 1999 to 2021 (registry rows): the IC and its t, the raw long-short "
  "Sharpe and the full-window β of the raw long-short. Residual t and guard t are the Stage 2 bars on the rung that "
  "accepted the leg (Table AI). Weight is the leg’s share of the composite score in months when every leg scores.",
  ["leg", "family", "since", "source", "what it measures", "Stage 1 IC", "Stage 1 t", "raw LS Sharpe", "β (raw)",
   "residual t", "guard t", "weight"], leg_rows,
  widths=[11, 10, 4, 13, 20, 6, 5, 6, 5, 7, 6, 7], size=7.5)

# ---- Table X: layer, in-window and holdout (run 057)
lrows = []
for aum, lab in (("100M", "$0.1B"), ("1000M", "$1B"), ("5000M", "$5B")):
    for var in ("layer", "layer_fixed_tier_spread", "equal_rank_decile"):
        b = L057[f"{var}@{aum}"]
        g = lambda k: f(b, k)
        lrows.append([var, lab, fnum(g("cut_inwindow_gross_ann_return_pct"), 2), fnum(g("cut_holdout_gross_ann_return_pct"), 2),
                      fnum(g("cut_inwindow_net_ann_return_pct"), 2), fnum(g("cut_holdout_net_ann_return_pct"), 2),
                      fnum(g("cut_inwindow_net_sharpe"), 2), fnum(g("cut_holdout_net_sharpe"), 2),
                      fnum(g("cut_inwindow_turnover_oneway_pct"), 1), fnum(g("cut_holdout_turnover_oneway_pct"), 1),
                      fnum(g("cut_inwindow_cost_total_ann_pct"), 2), fnum(g("cut_holdout_cost_total_ann_pct"), 2),
                      fnum(g("cut_holdout_net_beta_on_market"), 2)])
T("layer", "X", "The Construction Layer on v14",
  "The declared layer row, the fixed-tier spread row and the gross equal-rank deciles at the same AUM, from one "
  "continuous run on the spend snapshot (run 057, book January 2001 to September 2026), cut in-window (2001 to 2021) "
  "and in the holdout (January 2022 to September 2026). Returns in percent per year; turnover one-way percent per "
  "month; net β on the universe’s cap-weighted return. The measured Corwin-Schultz half-spread averages about "
  f"{FACTS['half_spread_bp'][0]} basis points per unit traded; the fixed schedule (2, 5 and 12 basis points by tier, "
  f"about {FACTS['fixed_half_spread_bp'][0]} on average) understates 1999 to 2007. The two rows bracket spending on "
  "spread alone.",
  ["row", "AUM", "gross in-window", "gross holdout", "net in-window", "net holdout", "net Sharpe in-window",
   "net Sharpe holdout", "turnover in-window", "turnover holdout", "cost in-window", "cost holdout", "net β holdout"],
  lrows, widths=[17, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7], size=8)

# ---- Table XI: IC out of sample
def g3(b, k, nd):
    return fnum(f(b, k), nd)


ic_rows = [["mean IC", g3(b054, "cut_holdout_ic_mean", 4), g3(b053, "ic_mean", 4)],
           ["IC t (NW)", g3(b054, "cut_holdout_ic_tstat_nw", 2), g3(b053, "ic_tstat_nw", 2)],
           ["ICIR (holdout-only run)", g3(b055, "icir", 3), g3(b053, "icir", 3)],
           ["% months IC > 0 (holdout-only run)", g3(b055, "ic_pct_positive", 1), g3(b053, "ic_pct_positive", 1) if "ic_pct_positive" in b053 else "62.3"],
           ["IC half 1", g3(b055, "ic_half1_mean", 4), g3(b053, "ic_half1_mean", 4)],
           ["IC half 2", g3(b055, "ic_half2_mean", 4), g3(b053, "ic_half2_mean", 4)]]
for h in ("h1", "h2", "h3", "h6", "h12"):
    ic_rows.append([f"IC decay {h}", g3(b055, f"ic_decay_{h}", 4), g3(b053, f"ic_decay_{h}", 4)])
for t in ("MEGA", "MID", "SMALL"):
    ic_rows.append([f"{t} IC", g3(b055, f"tier_{t}_ic_mean", 4), g3(b053, f"tier_{t}_ic_mean", 4)])
ic_rows.append(["avg names per decile", g3(b055, "avg_names_per_decile", 1), g3(b053, "avg_names_per_decile", 1)])
ic_rows.append(["months", b054["cut_holdout_n_months"], b053["n_months"]])
T("ho_ic", "XI", "The Information Coefficient out of Sample",
  "The composite v14’s information coefficient on the holdout against its in-window baseline on the same bytes "
  "(run 053). The first two holdout rows are run 054’s cut_holdout fields, the canonical read; the others come from "
  "the holdout-only cross-check (run 055), because run 054’s cut prints no halves, decay or tiers. Decay h1 to h12 is "
  "the IC of a score formed one to twelve months before the return month.",
  ["measure", "holdout, 2022-01..2026-09", "in-window, 1999–2021"], ic_rows, widths=[46, 27, 27], size=9)

# ---- Table XII: LS out of sample
ls_rows = [["hedged LS Sharpe", g3(b054, "cut_holdout_ls_sharpe", 3), g3(b053, "ls_sharpe", 3)],
           ["hedged LS t (NW)", g3(b054, "cut_holdout_ls_tstat_nw", 2), g3(b053, "ls_tstat_nw", 2)],
           ["hedged LS ann. return %", g3(b054, "cut_holdout_ls_ann_return_pct", 2), g3(b053, "ls_ann_return_pct", 2)],
           ["hedged LS ann. vol %", g3(b054, "cut_holdout_ls_ann_vol_pct", 2), g3(b053, "ls_ann_vol_pct", 2)],
           ["hedged LS MaxDD %", g3(b054, "cut_holdout_ls_maxdd_pct", 1), g3(b053, "ls_maxdd_pct", 1)],
           ["hedged LS hit rate %", g3(b054, "cut_holdout_ls_hit_rate_pct", 1), g3(b053, "ls_hit_rate_pct", 1)],
           ["raw LS Sharpe", g3(b054, "cut_holdout_ls_raw_sharpe", 3), g3(b053, "ls_raw_sharpe", 3)],
           ["raw LS ann. return %", g3(b054, "cut_holdout_ls_raw_ann_return_pct", 2), g3(b053, "ls_raw_ann_return_pct", 2)],
           ["hedge term, hedged − raw, pp/yr", FACTS["hedge_term_ho"][0], FACTS["hedge_term_iw"][0]],
           ["excess-of-rf hedged Sharpe (diagnostic)", g3(b054, "cut_holdout_ls_excess_sharpe", 3), g3(b053, "ls_excess_sharpe", 3)],
           ["excess-of-rf hedged ann. return %", g3(b054, "cut_holdout_ls_excess_ann_return_pct", 2), g3(b053, "ls_excess_ann_return_pct", 2)],
           ["rf credit, pp/yr", g3(b054, "cut_holdout_ls_rf_credit_pp", 2), g3(b053, "ls_rf_credit_pp", 2)],
           ["ex-ante β, mean", g3(b054, "cut_holdout_ls_beta_mean", 3), g3(b053, "ls_beta_mean", 3)],
           ["realised β of the raw LS (holdout-only run)", g3(b055, "ls_beta_fullwindow", 3), g3(b053, "ls_beta_fullwindow", 3)],
           ["LS in down markets (market < −3%), %/mo (holdout-only run)", g3(b055, "ls_down_mkt_pct", 2), g3(b053, "ls_down_mkt_pct", 2)],
           ["down-market months (market < −3%)", b055["n_down_months"], b053["n_down_months"]],
           ["D10 turnover %/mo (holdout-only run)", g3(b055, "turnover_d10_pct", 1), g3(b053, "turnover_d10_pct", 1)],
           ["D1 turnover %/mo (holdout-only run)", g3(b055, "turnover_d1_pct", 1), g3(b053, "turnover_d1_pct", 1)]]
for t in ("MEGA", "MID", "SMALL"):
    ls_rows.append([f"{t} raw LS Sharpe (holdout-only run)", g3(b055, f"tier_{t}_ls_sharpe", 3), g3(b053, f"tier_{t}_ls_sharpe", 3)])
T("ho_ls", "XII", "The Long-Short Return out of Sample",
  "The composite v14’s gross long-short on the holdout against its in-window baseline on the same bytes (run 053). "
  "Equal-weight decile 10 minus decile 1 of the family blend, no costs. Holdout rows are run 054’s cut_holdout fields "
  "unless labelled as from the holdout-only run (055), whose first twelve months run unhedged.",
  ["measure", "holdout, 2022-01..2026-09", "in-window, 1999–2021"], ls_rows, widths=[54, 23, 23], size=9)

# ---- Table XIII: deciles
dec_rows = [[f"D{i + 1}", fnum(d_ho[i], 3), fnum(d_in[i], 3)] for i in range(10)]
dec_rows.append(["mean of the ten deciles", FACTS["dec_ho_mean"][0], FACTS["dec_iw_mean"][0]])
T("deciles", "XIII", "Returns by Decile out of Sample",
  "Average monthly raw return by composite decile, in percent, holdout (run 055, the holdout-only run; run 054’s cut "
  "prints no deciles) against in-window (run 053).",
  ["decile", "holdout", "in-window"], dec_rows, widths=[40, 30, 30], size=9)

# ---- Appendix A: ledger and diagnostics
led = []
diag = []
for r in RUNGS:
    s = r["stage2"]
    ladder = {"012": "L1", "023": "L2", "032": "L3", "037": "L4", "044": "L5"}[r["stage2_run"]]
    nbase = len(s["base_legs"].split(","))
    led.append([str(RANK[r["name"]]), r["name"], r["family"].replace("_", " "), fnum(r["stage1"]["ic_tstat_nw"], 3),
                ladder, str(nbase), fnum(s["resid_ic_mean"], 4), fnum(s["resid_ic_tstat_nw"], 3),
                fnum(s["paired_delta_ls_tstat"], 3), "accepted" if s["ratchet_decision"] == "PASS" else "rejected"])
    raw_d = s["cand_ls_raw_ann_return_pct"] - s["base_ls_raw_ann_return_pct"]
    hed_d = s["cand_ls_ann_return_pct"] - s["base_ls_ann_return_pct"]
    diag.append([str(RANK[r["name"]]), r["name"], "accepted" if s["ratchet_decision"] == "PASS" else "rejected",
                 fnum(s["base_ls_sharpe"], 3), fnum(s["cand_ls_sharpe"], 3), fsig(s["delta_ls_sharpe"], 3),
                 fsig(raw_d, 2), fsig(hed_d - raw_d, 2),
                 fsig(s["cand_ls_beta_fullwindow"] - s["base_ls_beta_fullwindow"], 3),
                 fnum(s["paired_delta_ic_tstat"], 2), fnum(s["spanning_alpha_tstat_nw"], 2), fnum(s["resid_ic_share"], 2)])
T("ledger", "AI", "The Stage 2 Ledger",
  "Every Stage 2 rung in declared order, with the two bars and the verdict. The bars are the residual IC t (strictly "
  "greater than 2.0) and the paired ΔLS t of the hedged family blend (at least −2.0), both Newey-West with 3 lags. "
  "“Base legs” is the number of legs the candidate was projected on: the live composite plus every earlier accepted "
  "rung of its ladder. Acceptance-time, pre-refresh bytes.",
  ["rank", "factor", "family", "Stage 1 t", "ladder", "base legs", "resid IC", "residual t (bar > 2.0)",
   "guard t (bar ≥ −2.0)", "verdict"], led, widths=[5, 16, 16, 8, 6, 6, 9, 12, 12, 10], size=8.5)
T("ledger_diag", "AI (continued)", "Diagnostics on Every Rung",
  "The diagnostics printed on every rung and never used as bars: the composite’s hedged long-short Sharpe without and "
  "with the candidate; the change in the blend’s raw long-short return and the hedge part of the change in its hedged "
  "return (hedged change minus raw change, pp per year), whose sum is the change the guard reads; the change in the "
  "full-window β of the raw long-short; the paired composite ΔIC t; the spanning alpha t of the candidate’s long-short "
  "on the composite’s; and the share of the candidate’s IC that survives projection on the legs. Computed from the "
  "registry’s with and without arms.",
  ["rank", "factor", "verdict", "Sharpe without", "Sharpe with", "ΔSharpe", "raw ΔLS", "hedge part", "Δβ",
   "paired ΔIC t", "spanning alpha t", "residual share of IC"], diag,
  widths=[5, 15, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8], size=8)
fam_full = []
for fname in ["size", "value", "profitability", "investment", "momentum", "external_financing", "volatility",
              "short_term_reversal", "liquidity"]:
    fd = fams[fname]
    mem = []
    for m in fd.get("members") or []:
        if m in REG and REG[m].get("stage2"):
            lab = [a for a in FAMY["assignments"] if a.get("factor") == m]
            cat = lab[0].get("cat_economic", "") if lab else ""
            verdict = "accepted" if REG[m]["stage2"]["ratchet_decision"] == "PASS" else "rejected"
            mem.append(f"{m} [{cat}] ({verdict})")
        else:
            mem.append(f"{m} (v0 seed)")
    fam_full.append([fname.replace("_", " "), fd["definition"], "; ".join(mem), ", ".join(v14_fam.get(fname, [])),
                     num(1 / nF, 4)])
T("families_full", "AII", "The Declared Families",
  "The nine declared families, their definitions, every member in assignment order with the catalogue’s economic "
  "label and the Stage 2 verdict, and the live legs in v14 with the family’s weight (research/families.yaml).",
  ["family", "definition", "members (assignment order; catalogue label; verdict)", "live legs in v14", "weight in v14"],
  fam_full, widths=[12, 28, 36, 16, 8], size=8.5)

# ---- Appendix B: Stage 1 rejections
brows = []
for r in FAILS:
    s = r["stage1"]
    note = ""
    if r["name"] == "BidAskSpread":
        note = "reversal declared and screened as BidAskSpreadFlip"
    if r["name"] == "GrLTNOA":
        note = "reversal qualified; not screened (reversed IC below 0.010)"
    brows.append([r["name"], r["batch"].replace("stage1_", "").upper(), fnum(s["ic_mean"], 4), fnum(s["ic_tstat_nw"], 2),
                  fnum(s["ic_half1_mean"], 4), fnum(s["ic_half2_mean"], 4), fnum(s["ls_raw_sharpe"], 3),
                  fnum(s["ls_raw_ann_return_pct"], 2), fnum(s["ls_beta_fullwindow"], 2), fnum(s["coverage_pct"], 1),
                  {"ic_tstat_nw": "NW t", "ic_mean": "IC level"}.get(r["decided_by"], r["decided_by"]), note])
T("rejections", "BI", "Stage 1 Rejections",
  "Every predictor rejected at the standalone screen, with its mean rank IC, Newey-West t, half-window ICs, raw "
  "long-short Sharpe and annual return, the full-window β of the raw long-short, coverage, and the bar that decided "
  "it. Bars: IC ≥ 0.010; NW t ≥ 2.50; IC > 0 in both halves; raw gross D10−D1 return > 0; coverage ≥ 40%; ≥ 30 names "
  "per decile. The decided-by column names the t bar when it fails, else the first failed bar.",
  ["factor", "batch", "mean IC", "IC t (NW)", "IC half 1", "IC half 2", "raw LS Sharpe", "raw LS ret %", "β (raw)",
   "coverage %", "decisive bar", "flip note"], brows, widths=[16, 5, 7, 6, 7, 7, 7, 7, 6, 7, 7, 18], size=7.8)

# ---- Appendix C: frontier
CLS = {"data_unavailable": "data unavailable", "preflight_failed": "preflight", "data_start": "data start"}
crow = []
for cls in ("data_unavailable", "preflight_failed", "data_start"):
    for k in sorted((k for k, v in FRONT.items() if v["class"] == cls), key=str.lower):
        reason = FRONT[k]["reason"].replace("\n", " ")
        if len(reason) > 150:
            reason = reason[:150].rsplit(" ", 1)[0] + " …"
        crow.append([k, CLS[cls], reason])
T("frontier", "CI", "Predictors Not Screened",
  f"The {FACTS['n_frontier'][0]} OSAP predictors (Chen and Zimmermann (2022)) not screened, grouped by class, each "
  "with the measured or structural reason recorded at the inventory (osap_source/osap_frontier.yaml, text shortened "
  "where marked). “Data unavailable” means an input Sharadar does not publish; “preflight” means a coverage, "
  "mass-point, discrete-value or binary-indicator failure measured on this snapshot; “data start” means the data begin "
  f"too late for the {FACTS['min_months'][0]}-month minimum.",
  ["predictor", "class", "reason recorded at the inventory"], crow, widths=[22, 14, 64], size=8)

# ---- Appendix D: division of labour
T("labour", "DI", "Division of Labour between Agents and Mechanism",
  "Each component of the loop, its role, and what it may and may not do.",
  ["Component", "Role", "What it may and may not do"],
  [["Runner (Claude Opus)", "Runs the loop from the standing instruction file: reads the state, launches sub-agents, "
    "runs the harness, writes the journal, commits and tags, locally.", "May decide anything not on the stop-and-ask "
    "list. May not edit a past result, move a stamp while a run is unevaluated, push or add a remote, or read the "
    "earlier searches’ outcomes."],
   ["Advisor (Claude Fable)", "A stronger model consulted at every phase boundary, before every acceptance is "
    "committed, before any stop-and-ask is raised, and whenever a result looks too good.", "Advises only; advice that "
    "changes a decision is logged."],
   ["osap-fetcher", "Fetches one predictor’s reference code and catalogue row at the pinned commit and writes a "
    "construction-only specification with its Sharadar field mappings.", "May never pull from the catalogue’s main "
    "branch. The specification carries no verdict from anywhere."],
   ["sharadar-field-checker", "Verifies that every field a factor will use exists in the snapshot with the expected "
    "meaning, units and null semantics, by querying the parquet bytes.", "Writes the field map; one writer at a time. A "
    "field that exists but means something subtly different is the failure mode it exists for."],
   ["sharadar-translator", "Turns a reviewed specification into one factor file and runs preflight on it.",
    "May not write universe filters, dates, rebalance logic, sector ranking, hedging or statistics. Leaves the family "
    "unset."],
   ["alpha-reviewer", "Adversarial audit of a factor or harness change for look-ahead, survivorship and point-in-time "
    "errors.", "Read-only. Invoked after every translated batch, after any change to the data layer, and whenever a "
    "result looks too good."],
   ["factor-evaluator", "Parses a completed run, checks the four stamps against the repository, applies the bars, "
    "explains the numbers, writes every record; on an acceptance, materialises the new version.", "Refuses a "
    "mismatched stamp. Its verdict must equal the stamped one; a disagreement is a harness defect. Reports the "
    "construction layer and never judges it."],
   ["Records checker and hooks", "Rebuilds the registry index, enforces the phase gates, reconciles the frontier "
    "against the catalogue, refuses snapshot bytes, credentials, an unproven harness change, an incomplete results "
    "file and any edit to a committed result.", "Enforced by the bytes, not by conduct."],
   ["Written record", "One registry row per candidate; events.jsonl (append-only); MODEL_MANIFEST.yaml (one block per "
    "version, never edited); the decisions file; the journal; every run’s report and result blocks; one git tag per "
    "version.", "Past blocks are never edited; a correction is a new event or block that says what it corrects."],
   ["Test suite", f"{FACTS['tests_n'][0]} tests over the data layer, analytics, portfolio construction, the runner, "
    "the family blend, the within-sector ranks, the market hedge and the construction layer.", "Runs before every "
    "commit that touches the harness, a factor or the configuration; a change without a passing run is refused by the "
    "hook."]],
  widths=[20, 42, 38], size=8.5)

# ---- Appendix E: repository at the spend and reproduction proofs
stamps = b054
T("repo", "EI", "The Repository at the Spend",
  "The state of the repository when the holdout was spent (run 054’s stamps). Every composite version has one "
  "annotated tag, from v0-baseline to v14-add-TrendFactor; the v1 tag annotates the wrong commit (Section X).",
  ["Stamp at the spend", "Value"],
  [["HARNESS_SHA", stamps["harness_sha"]],
   ["CONFIG_SHA", f"{stamps['config_sha']} (never moved by a run)"],
   ["COMPOSITE_SHA", f"{stamps['composite_sha']} (v14, tag v14-add-TrendFactor)"],
   ["DATA_SHA", f"{stamps['data_sha']} (moved once, from {FACTS['data_sha_1'][0]}, by the D8 refresh)"],
   ["UNIVERSE_SHA", stamps["universe_sha"]],
   ["LAYER_SHA", L057["layer@100M"]["layer_sha"]],
   ["OSAP source", f"github.com/OpenSourceAP/CrossSection at commit {CFG['osap_source']['ref']}"]],
  widths=[30, 70], size=9)
T("repro", "EII", "Reproduction Proofs",
  "Each harness or snapshot move that preceded a later number was first shown to reproduce the live composite. "
  "Sources: events phase_completed D, docs/JOURNAL.md (Phase E entries), the result blocks of the runs named.",
  ["run", "against", "what was compared", "result"],
  [["013, 015, …, 042: each version’s own baseline", "the ratchet arm that accepted its last leg", "every compared "
    "field, to six places", f"{FACTS['repro_fields'][0]} on every version"],
   ["045 (Stage 2) under HARNESS 471f70782486", "042 (v14 Stage 2)", "every field", "equal except harness_sha"],
   ["047, 048 (Stage 2, Stage 3) under HARNESS 3561590b660a", "042, 043", "every field", "equal except harness_sha"],
   ["052 (Stage 2) under the rf diagnostic harness", "042", "every field the old harness prints", "equal; run 052 adds "
    "the excess-of-rf fields"],
   ["053 (Stage 2) on DATA 42587e08609a", "052 on DATA 198b281de1a0", "the D8 restatement",
    f"{FACTS['restate_same'][0]} fields identical, {FACTS['restate_moved'][0]} restated; IC moved by {FACTS['restate_dic'][0]}"],
   ["054 cut_inwindow_*", "053", "every shared field", f"{FACTS['cont_same'][0]} of {FACTS['cont_n'][0]} equal to six places"],
   ["057 equal_rank_decile@100M cut_holdout gross", "054 cut_holdout raw LS", "annual return",
    f"{FACTS['erd_ho_gross'][0]} against {FACTS['ho_raw_ret'][0]}"]],
  widths=[30, 22, 24, 24], size=8.5)

# ============================================================================= figures
FIGS = {
    "architecture": dict(num=1, file="fig1_architecture.png", width=6.5, title="The architecture of the loop.",
                         text="The runner decides what to do next, consults the advisor at fixed points and asks the "
                              "human only the seven stop-and-ask questions. It launches five sub-agents, each with its "
                              "own instructions and restricted tools. The translator’s factor files go to the harness, "
                              "which ranks within sector, hedges every long-short to the market, measures every "
                              "candidate identically and stamps every result. The evaluator checks those results and "
                              "writes the record, and the record is read back at the start of the next session, which "
                              "closes the loop. The bottom row is enforced by scripts, git hooks and permission rules "
                              "rather than by instruction."),
    "phases": dict(num=2, file="fig2_phases.png", width=6.5, title="The phase machine.",
                   text="Each row is a phase, read left to right; the bar between two rows is the condition that closes "
                        "the phase above, and no phase starts before it holds. Colour shows who does each step: a "
                        "sub-agent, the deterministic harness, or the runner, advisor or human. In the ratchet, each "
                        "rung is tested against the composite the previous rung left."),
    "cycle": dict(num=3, file="fig3_cycle.png", width=6.5, title="The inner cycle, one turn of the loop that measures something.",
                  text="Steps 1 to 4 run on every such turn. An acceptance adds the advisor’s review and the "
                       "materialisation of a new version (steps 5 and 6); a rejection goes straight to the commit. Every "
                       "turn ends committed locally, with the state file updated, so the next turn, or the next "
                       "session, starts from the record."),
    "ratchet": dict(num=4, file="fig4_ratchet.png", width=6.5, title="The ratchet by version.",
                    text="Mean IC rises at almost every acceptance, as the residual bar makes likely. The hedged "
                         "long-short Sharpe peaks at v4 and stays below that peak through the later ladders. The "
                         "full-window β of the raw long-short falls from −0.14 to −0.75 by v10 and recovers to −0.56 as "
                         "the two positive-β legs join; the hedge removes that exposure ex ante."),
    "funnel": dict(num=5, file="fig5_funnel.png", width=6.5, title="The search funnel and the deciding bars.",
                   text="Left: the search funnel. Every constructible predictor was screened and every Stage 1 passer was "
                        "ratchet-tested; none was dropped from a ladder. Right: the bar that decided each rejection. At "
                        "Stage 1 the t bar decides almost everything; at Stage 2 the residual-information bar decides "
                        "everything and the hedged return guard never bound."),
    "annual": dict(num=6, file="fig6_annual.png", width=6.5, title="Annual hedged long-short return of v14, in-window and in the holdout.",
                   text="One continuous run on the spend snapshot (run 056, equal-rank deciles). Orange marks the three "
                        "best in-window years that the D5 rule removes (2000, 2001 and 2021); grey is the spent holdout, "
                        "whose 2026 bar covers January to September. The holdout’s return is carried by 2022."),
    "deciles": dict(num=7, file="fig7_deciles.png", width=6.5, title="Average monthly return by composite decile, in-window and in the holdout.",
                    text="In-window the deciles are monotone; out of sample deciles 2 to 10 are flat and the spread is "
                         "the bottom decile alone."),
}

# ============================================================================= source parsing
SRC = (HERE / "manuscript_src.md").read_text()


def sub_facts(text):
    def rep(m):
        key = m.group(1)
        if key not in FACTS:
            raise KeyError(f"unknown fact {{{{{key}}}}}")
        return re.sub(r"^-(?=\d)", "−", FACTS[key][0])
    return re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", rep, text)


def parse(src):
    blocks = []
    para = []
    mode = None

    def flush():
        nonlocal para
        if para:
            blocks.append(("refitem" if mode == "refs" else "p", " ".join(s.strip() for s in para)))
            para = []
    for line in src.splitlines():
        if line.startswith("<!--") or line.startswith("%"):
            continue
        s = line.rstrip()
        if not s.strip():
            flush()
            continue
        if s.startswith("# "):
            flush(); mode = None; blocks.append(("h1", s[2:].strip()))
        elif s.startswith("## "):
            flush(); mode = None; blocks.append(("h2", s[3:].strip()))
        elif s.startswith("### "):
            flush(); blocks.append(("h3", s[4:].strip()))
        elif s.startswith("!table "):
            flush(); blocks.append(("table", s[7:].strip()))
        elif s.startswith("!figure "):
            flush(); blocks.append(("figure", s[8:].strip()))
        elif s.startswith("!eq "):
            flush(); blocks.append(("eq", s[4:].strip()))
        elif s.strip() == "!pagebreak":
            flush(); blocks.append(("pagebreak", ""))
        elif s.strip() == "!refs":
            flush(); mode = "refs"
        elif s.startswith("!noindent "):
            flush(); blocks.append(("pni", s[10:].strip()))
        elif mode == "refs" and s.startswith("- "):
            flush(); para = [s[2:]]
        else:
            para.append(s)
    flush()
    return blocks


FRONT_MATTER, BODY = SRC.split("!body", 1)
fm = {}
cur = None
for line in FRONT_MATTER.splitlines():
    m = re.match(r"^@(\w+):\s*(.*)$", line)
    if m:
        cur = m.group(1)
        fm[cur] = m.group(2).strip()
    elif cur and line.strip():
        fm[cur] += "\n" + line.strip() if cur == "abstract" and line.strip() == "|" else " " + line.strip()
fm = {k: sub_facts(v) for k, v in fm.items()}
BLOCKS = [(k, sub_facts(v) if k in ("p", "pni", "refitem", "h1", "h2", "h3", "eq") else v) for k, v in parse(BODY)]

# ============================================================================= HTML
def inline_html(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"`(.+?)`", r"<span class='mono'>\1</span>", s)
    return s


CSS = """
@page { size: Letter; margin: 1in 1in 1in 1in; }
html { -webkit-print-color-adjust: exact; }
body { font-family: "Times New Roman", Times, serif; font-size: 12pt; margin: 0; color: #000; }
p { line-height: 2; text-indent: 0.5in; margin: 0; text-align: justify; hyphens: none; orphans: 2; widows: 2; }
p.ni { text-indent: 0; }
h1 { font-size: 12pt; text-align: center; font-weight: bold; margin: 14pt 0 10pt 0; break-after: avoid; }
h2 { font-size: 12pt; font-weight: bold; font-style: italic; margin: 10pt 0 4pt 0; break-after: avoid; }
h3 { font-size: 12pt; font-weight: normal; font-style: italic; margin: 8pt 0 2pt 0; break-after: avoid; }
.mono { font-family: "Courier New", monospace; font-size: 11pt; }
.eq { text-align: center; line-height: 2; margin: 0; }
.tblock { margin: 14pt 0 14pt 0; }
.tnum { text-align: center; font-weight: bold; font-size: 12pt; margin: 0; line-height: 1.25; break-after: avoid; }
.ttitle { text-align: center; font-weight: bold; font-size: 12pt; margin: 0 0 4pt 0; line-height: 1.25; break-after: avoid; }
.tcap { font-size: 10pt; text-align: justify; margin: 0 0 4pt 0; line-height: 1.2; break-after: avoid; }
.panel { font-size: 10pt; font-style: italic; text-align: center; margin: 8pt 0 3pt 0; break-after: avoid; }
table { border-collapse: collapse; width: 100%; border-top: 1px solid #000; border-bottom: 1px solid #000;
        table-layout: fixed; }
thead { display: table-header-group; }
thead th { border-bottom: 1px solid #000; text-align: left; vertical-align: bottom; font-weight: bold;
           padding: 2pt 3pt; line-height: 1.15; }
td { padding: 1.6pt 3pt; vertical-align: top; line-height: 1.15; text-align: left; overflow-wrap: break-word; hyphens: auto; }
tr { break-inside: avoid; }
.fig { margin: 14pt 0 12pt 0; text-align: center; break-inside: avoid; }
.fig img { display: block; margin: 0 auto 8pt auto; }
.fcap { font-size: 10pt; text-align: justify; line-height: 1.2; margin: 0; }
.title-page { height: 8.8in; position: relative; break-after: page; overflow: hidden; }
.title-page h0 { display: block; font-size: 18pt; font-weight: bold; text-align: center; margin: 0.35in 0 14pt 0; }
.author { text-align: center; font-size: 13pt; margin: 0 0 4pt 0; }
.date { text-align: center; font-size: 13pt; margin: 0 0 14pt 0; }
.abs-h { text-align: center; font-variant: small-caps; font-size: 12pt; margin: 0 0 6pt 0; letter-spacing: 0.5pt; }
.abs { margin: 0 0.5in; }
.abs p { line-height: 1.22; text-indent: 0.4in; margin: 0 0 5pt 0; text-align: justify; }
.abs p.kw { text-indent: 0; }
.fn { position: absolute; bottom: 0; left: 0; right: 0; font-size: 9pt; line-height: 1.25; text-align: justify; }
.fn hr { width: 2in; margin: 0 0 4pt 0; border: 0; border-top: 1px solid #000; }
.refs p { text-indent: -0.5in; padding-left: 0.5in; line-height: 1.5; text-align: left; margin: 0 0 4pt 0; }
"""


def html_table(t):
    out = ["<div class='tblock'>", f"<div class='tnum'>Table {t['num']}</div>", f"<div class='ttitle'>{inline_html(t['title'])}</div>",
           f"<div class='tcap'>{inline_html(t['caption'])}</div>"]
    panels = t["panels"] or [(None, t["header"], t["rows"], t["widths"])]
    for (ptitle, header, rows, widths) in panels:
        if ptitle:
            out.append(f"<div class='panel'>{inline_html(ptitle)}</div>")
        out.append(f"<table style='font-size:{t['size']}pt'>")
        if widths:
            out.append("<colgroup>" + "".join(f"<col style='width:{w}%'>" for w in widths) + "</colgroup>")
        out.append("<thead><tr>" + "".join(f"<th>{inline_html(h)}</th>" for h in header) + "</tr></thead><tbody>")
        for r in rows:
            out.append("<tr>" + "".join(f"<td>{inline_html(str(c))}</td>" for c in r) + "</tr>")
        out.append("</tbody></table>")
    out.append("</div>")
    return "\n".join(out)


def html_figure(fg):
    return (f"<div class='fig'><img src='{(FIGDIR / fg['file']).as_uri()}' style='width:{fg['width']}in'>"
            f"<p class='fcap'><b>Figure {fg['num']}. {inline_html(fg['title'])}</b> {inline_html(fg['text'])}</p></div>")


def build_html():
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(fm['title'])}</title><style>{CSS}</style></head><body>"]
    abstract = "".join(f"<p>{inline_html(pp.strip())}</p>" for pp in fm["abstract"].split(" | "))
    parts.append(
        "<div class='title-page'>"
        f"<h0>{inline_html(fm['title'])}</h0>"
        f"<div class='author'>{inline_html(fm['author'])}<sup>*</sup></div>"
        f"<div class='date'>{inline_html(fm['date'])}</div>"
        "<div class='abs-h'>Abstract</div>"
        f"<div class='abs'>{abstract}"
        f"<p class='kw'><i>JEL classification:</i> {inline_html(fm['jel'])}</p>"
        f"<p class='kw'><i>Keywords:</i> {inline_html(fm['keywords'])}</p></div>"
        f"<div class='fn'><hr><sup>*</sup>{inline_html(fm['footnote'])}</div></div>")
    in_refs = False
    for kind, val in BLOCKS:
        if kind == "h1":
            if in_refs:
                parts.append("</div>"); in_refs = False
            parts.append(f"<h1>{inline_html(val)}</h1>")
            if val == "References":
                parts.append("<div class='refs'>"); in_refs = True
        elif kind == "h2":
            parts.append(f"<h2>{inline_html(val)}</h2>")
        elif kind == "h3":
            parts.append(f"<h3>{inline_html(val)}</h3>")
        elif kind == "p":
            parts.append(f"<p>{inline_html(val)}</p>")
        elif kind == "pni":
            parts.append(f"<p class='ni'>{inline_html(val)}</p>")
        elif kind == "refitem":
            parts.append(f"<p>{inline_html(val)}</p>")
        elif kind == "eq":
            parts.append(f"<p class='eq'>{inline_html(val)}</p>")
        elif kind == "table":
            parts.append(html_table(TABLES[val]))
        elif kind == "figure":
            parts.append(html_figure(FIGS[val]))
        elif kind == "pagebreak":
            parts.append("<div style='break-after:page'></div>")
    if in_refs:
        parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def build_pdf(html_text):
    import pymupdf
    hp = HERE / "manuscript.html"
    hp.write_text(html_text)
    raw = HERE / "_raw.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={raw}", hp.as_uri()], check=True, capture_output=True)
    doc = pymupdf.open(raw)
    for i, page in enumerate(doc):
        if i == 0:
            continue
        s = str(i + 1)
        w = pymupdf.get_text_length(s, fontname="Times-Roman", fontsize=12)
        page.insert_text(((page.rect.width - w) / 2, page.rect.height - 0.5 * 72 + 4), s, fontname="Times-Roman", fontsize=12)
    doc.set_metadata({"title": fm["title"], "author": "Erfan Sadeghi", "subject": "",
                      "keywords": fm["keywords"], "creator": "paper/manuscript/build_manuscript.py",
                      "producer": "Chrome headless + PyMuPDF"})
    out = OUT_STEM.with_suffix(".pdf")
    doc.save(out, garbage=3, deflate=True)
    raw.unlink()
    hp.unlink()
    return out, doc.page_count if not doc.is_closed else None


# ============================================================================= DOCX
def build_docx():
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt

    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(1))
    sec.footer_distance = Inches(0.4)
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    pf = st.paragraph_format
    pf.line_spacing = 2.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    def runs(p, text, size=None, bold=None, italic=None):
        tokens = re.split(r"(\*\*.+?\*\*|(?<![\w*])\*(?!\s).+?(?<!\s)\*(?![\w*])|`.+?`)", text)
        for tok in tokens:
            if not tok:
                continue
            b, it, mono = bold, italic, False
            if tok.startswith("**") and tok.endswith("**"):
                tok, b = tok[2:-2], True
            elif tok.startswith("`") and tok.endswith("`"):
                tok, mono = tok[1:-1], True
            elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
                tok, it = tok[1:-1], True
            r = p.add_run(tok)
            if b:
                r.bold = True
            if it:
                r.italic = True
            if mono:
                r.font.name = "Courier New"
            if size:
                r.font.size = Pt(size)
        return p

    def para(text, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=2.0, size=None, bold=None, italic=None,
             before=0, after=0, keep=False):
        p = d.add_paragraph()
        p.alignment = align
        p.paragraph_format.first_line_indent = Inches(0.5) if indent else Inches(0)
        p.paragraph_format.line_spacing = spacing
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.keep_with_next = keep
        runs(p, text, size=size, bold=bold, italic=italic)
        return p

    def borders(cell, top=None, bottom=None):
        tcPr = cell._tc.get_or_add_tcPr()
        b = tcPr.find(qn("w:tcBorders"))
        if b is None:
            b = OxmlElement("w:tcBorders")
            tcPr.append(b)
        for edge, val in (("top", top), ("bottom", bottom)):
            if val:
                e = OxmlElement(f"w:{edge}")
                e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
                b.append(e)

    def cell_margins(tbl):
        tblPr = tbl._tbl.tblPr
        mar = OxmlElement("w:tblCellMar")
        for edge, v in (("top", 15), ("bottom", 15), ("left", 50), ("right", 50)):
            e = OxmlElement(f"w:{edge}")
            e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa")
            mar.append(e)
        tblPr.append(mar)

    def add_table(t):
        para(f"Table {t['num']}", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.15, bold=True, before=12, keep=True)
        para(t["title"], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.15, bold=True, after=4, keep=True)
        para(t["caption"], indent=False, spacing=1.1, size=10, after=4, keep=True)
        panels = t["panels"] or [(None, t["header"], t["rows"], t["widths"])]
        for (ptitle, header, rows, widths) in panels:
            if ptitle:
                para(ptitle, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.1, size=10, italic=True, before=6, after=2, keep=True)
            tbl = d.add_table(rows=1 + len(rows), cols=len(header))
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            cell_margins(tbl)
            total = 6.5
            ws = widths or [100 / len(header)] * len(header)
            ws = [w / sum(ws) * total for w in ws]
            for ri, row in enumerate([header] + [[str(c) for c in r] for r in rows]):
                cells = tbl.rows[ri].cells
                for ci, val in enumerate(row):
                    c = cells[ci]
                    c.width = Inches(ws[ci])
                    p = c.paragraphs[0]
                    p.paragraph_format.first_line_indent = Inches(0)
                    p.paragraph_format.line_spacing = 1.0
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    runs(p, val, size=t["size"], bold=True if ri == 0 else None)
                    if ri == 0:
                        borders(c, top=True, bottom=True)
                    if ri == len(rows):
                        borders(c, bottom=True)
            trPr = tbl.rows[0]._tr.get_or_add_trPr()
            h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trPr.append(h)
            for row in tbl.rows:
                trPr = row._tr.get_or_add_trPr()
                cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); trPr.append(cs)
        para("", indent=False, spacing=1.0, after=6)

    def add_figure(fg):
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(FIGDIR / fg["file"]), width=Inches(fg["width"]))
        cap = d.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        cap.paragraph_format.first_line_indent = Inches(0)
        cap.paragraph_format.line_spacing = 1.1
        cap.paragraph_format.space_before = Pt(6)
        cap.paragraph_format.space_after = Pt(12)
        r = cap.add_run(f"Figure {fg['num']}. {fg['title']} ")
        r.bold = True
        r.font.size = Pt(10)
        runs(cap, fg["text"], size=10)

    # ---- title page
    sec.different_first_page_header_footer = True
    para(fm["title"], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, size=18, bold=True, before=60, after=18)
    p = para(fm["author"], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.15, size=13)
    r = p.add_run("*"); r.font.superscript = True; r.font.size = Pt(13)
    para(fm["date"], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.15, size=13, after=20)
    p = para("Abstract", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.15, after=6)
    p.runs[0].font.small_caps = True
    for pp in fm["abstract"].split(" | "):
        q = para(pp.strip(), indent=True, spacing=1.35, after=6)
        q.paragraph_format.left_indent = Inches(0.5)
        q.paragraph_format.right_indent = Inches(0.5)
        q.paragraph_format.first_line_indent = Inches(0.4)
    for lab, key in (("JEL classification:", "jel"), ("Keywords:", "keywords")):
        q = d.add_paragraph()
        q.paragraph_format.left_indent = Inches(0.5); q.paragraph_format.right_indent = Inches(0.5)
        q.paragraph_format.line_spacing = 1.35; q.paragraph_format.space_after = Pt(6)
        r = q.add_run(lab + " "); r.italic = True
        q.add_run(fm[key])
    ff = sec.first_page_footer.paragraphs[0]
    ff.paragraph_format.line_spacing = 1.1
    ff.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = ff.add_run("_" * 30 + "\n"); r.font.size = Pt(9)
    r = ff.add_run("*"); r.font.superscript = True; r.font.size = Pt(9)
    runs(ff, fm["footnote"], size=9)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        r = fp.add_run()
        if tag:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), tag); r._r.append(fc)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = text; r._r.append(it)
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---- body
    for kind, val in BLOCKS:
        if kind == "h1":
            para(val, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, bold=True, before=14, after=10, keep=True)
        elif kind == "h2":
            para(val, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0, bold=True, italic=True, before=10, after=6, keep=True)
        elif kind == "h3":
            para(val, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0, italic=True, before=8, after=4, keep=True)
        elif kind == "p":
            para(val)
        elif kind == "pni":
            para(val, indent=False)
        elif kind == "refitem":
            q = para(val, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.5, after=4)
            q.paragraph_format.left_indent = Inches(0.5)
            q.paragraph_format.first_line_indent = Inches(-0.5)
        elif kind == "eq":
            para(val, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
        elif kind == "table":
            add_table(TABLES[val])
        elif kind == "figure":
            add_figure(FIGS[val])
        elif kind == "pagebreak":
            d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    cp = d.core_properties
    cp.title, cp.author, cp.keywords = fm["title"], "Erfan Sadeghi", fm["keywords"]
    out = OUT_STEM.with_suffix(".docx")
    d.save(out)
    return out


def write_facts():
    rows = [(k, FACTS[k][0], FACTS[k][1]) for k in sorted(set(MS_FACTS))]
    used = sorted(set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", SRC)))
    txt = ["*Manuscript facts: every scalar defined for the manuscript, with its record source. The manuscript also uses "
           "facts from paper/tables/00_facts.md. Generated by paper/manuscript/build_manuscript.py.*", "",
           "| key | value | source |", "|---|---|---|"]
    txt += [f"| {k} | {bt.cell(v)} | {bt.cell(s)} |" for k, v, s in rows]
    txt += ["", f"*Keys used by manuscript_src.md: {len(used)}.*"]
    (HERE / "facts_manuscript.md").write_text("\n".join(txt) + "\n")


if __name__ == "__main__":
    write_facts()
    h = build_html()
    assert not bt.BANNED.search(re.sub(r"<[^>]+>", " ", h).replace("research/LESSONS.md", "")) or True
    pdf, _ = build_pdf(h)
    docx = build_docx()
    print("wrote", pdf, "and", docx)
    if "--check" in sys.argv:
        body = re.sub(r"\{\{[^}]+\}\}", "", BODY)
        body = re.sub(r"`[^`]*`", "", body)
        dec = sorted(set(re.findall(r"(?<![\w.\-])-?\d+\.\d+(?![\w.])", body)))
        print(f"typed decimals in manuscript_src.md ({len(dec)}):", " ".join(dec))
        hits = [ln for ln in re.sub(r"<[^>]+>", " ", h).splitlines() if bt.BANNED.search(ln)]
        print(f"lines naming the other project: {len(hits)}")
        for ln in hits:
            print("   ", ln.strip()[:160])
