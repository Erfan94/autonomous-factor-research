#!/usr/bin/env python3
"""
Draw the manuscript's seven figures into paper/manuscript/figures/, from the records only.

    python3 paper/manuscript/build_figures.py

Figures 1-3 are diagrams of the framework. Figure 4 reads MODEL_MANIFEST.yaml (v0-v14 baselines),
Figure 5 the registry, Figure 6 run 056's equal_rank_decile annual returns (one continuous run,
1999-2026, on the spend snapshot), Figure 7 the decile returns of runs 053 and 055.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "paper"))
_argv = sys.argv
sys.argv = [sys.argv[0]]
import build_tables as bt  # noqa: E402
sys.argv = _argv

OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300, "svg.hashsalt": "v4",
                     "pdf.fonttype": 42})
BLUE, ORANGE, GREY = "#3b6ea5", "#c8742f", "#7f7f7f"
C = {"agent": ("#eaf1f8", "#5b8bc0"), "harness": ("#fbefe3", "#d0843f"), "people": ("#efefef", "#8a8a8a"),
     "files": ("#ffffff", "#8a8a8a"), "dark": ("#3a3a3a", "#3a3a3a")}


def box(ax, x, y, w, h, title, sub="", kind="people", tsize=7.6, ssize=6.6):
    fc, ec = C[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fc, ec=ec, lw=0.9))
    col = "white" if kind == "dark" else "#111111"
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=tsize, fontweight="bold", color=col)
        ax.text(x + w / 2, y + h * 0.32, sub, ha="center", va="center", fontsize=ssize, color=col if kind != "dark" else "#dddddd",
                linespacing=1.15, style="italic" if kind == "dark" else "normal")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=tsize, fontweight="bold", color=col)


def arrow(ax, x0, y0, x1, y1, both=False, color="#333333"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=0.8, shrinkA=0, shrinkB=0,
                                mutation_scale=7))


def label(ax, x, y, s, ha="center", size=6.4):
    ax.text(x, y, s, ha=ha, va="center", fontsize=size, style="italic", color="#444444",
            bbox=dict(fc="white", ec="none", pad=0.6))


def legend(ax, y, items):
    x = 0.02
    for kind, txt in items:
        fc, ec = C[kind]
        ax.add_patch(FancyBboxPatch((x, y - 0.009), 0.028, 0.018, boxstyle="round,pad=0.002,rounding_size=0.004", fc=fc, ec=ec, lw=0.8))
        ax.text(x + 0.036, y, txt, va="center", fontsize=6.6)
        x += 0.036 + 0.0088 * len(txt) + 0.035


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def fig1():
    fig, ax = canvas(6.5, 5.6)
    legend(ax, 0.975, [("agent", "sub-agent (language model)"), ("harness", "harness (deterministic code)"),
                       ("people", "runner, advisor or human"), ("files", "files and rules")])
    ax.text(0.02, 0.905, "Orchestration: what to do next", fontsize=8, fontweight="bold")
    box(ax, 0.02, 0.76, 0.26, 0.12, "Human", "the author: data licence,\ndesign rules; answers the\nstop-and-ask questions")
    box(ax, 0.37, 0.76, 0.26, 0.12, "Runner (Claude Opus)", "works from CLAUDE.md;\nlaunches sub-agents, runs\nthe harness, logs, commits")
    box(ax, 0.72, 0.76, 0.26, 0.12, "Advisor (Claude Fable)", "reviews the whole\ntranscript at fixed points;\nadvises only")
    arrow(ax, 0.28, 0.82, 0.37, 0.82, both=True); label(ax, 0.325, 0.845, "asks")
    arrow(ax, 0.63, 0.82, 0.72, 0.82, both=True); label(ax, 0.675, 0.845, "consults")
    ax.text(0.02, 0.705, "Sub-agents: specialised judgement", fontsize=8, fontweight="bold", zorder=5,
            bbox=dict(fc="white", ec="none", pad=0.8))
    xs = [0.02, 0.215, 0.41, 0.605, 0.80]
    names = [("osap-fetcher", "catalogue code to a\nconstruction spec"), ("field-checker", "verifies each field\non the data bytes"),
             ("translator", "spec to a factor file;\nruns preflight"), ("alpha-reviewer", "read-only audit of\neach batch"),
             ("factor-evaluator", "checks stamps,\nwrites records")]
    ax.plot([0.5, 0.5], [0.76, 0.735], color="#333", lw=0.8)
    ax.plot([xs[0] + 0.09, xs[-1] + 0.09], [0.735, 0.735], color="#333", lw=0.8)
    label(ax, 0.545, 0.745, "launches", ha="left")
    for x, (t, s) in zip(xs, names):
        arrow(ax, x + 0.09, 0.735, x + 0.09, 0.69)
        box(ax, x, 0.58, 0.18, 0.11, t, s, kind="agent")
    ax.text(0.02, 0.525, "Measurement and record", fontsize=8, fontweight="bold")
    box(ax, 0.02, 0.36, 0.50, 0.14, "Deterministic harness",
        "point-in-time universe, within-sector ranks, IC and Newey-West t,\ndeciles, the market hedge (ex-ante β), the "
        "registered bars;\nfour hashes on every result", kind="harness")
    box(ax, 0.66, 0.37, 0.32, 0.12, "Written record", "registry, event log, manifest,\njournal, tags, session state", kind="files")
    arrow(ax, 0.50, 0.58, 0.50, 0.50); label(ax, 0.55, 0.545, "factor files", ha="left")
    arrow(ax, 0.52, 0.43, 0.66, 0.43); label(ax, 0.59, 0.455, "stamped\nresults")
    arrow(ax, 0.89, 0.49, 0.89, 0.58, both=True); label(ax, 0.86, 0.535, "reads results, writes rows", ha="right")
    ax.plot([0.98, 0.995, 0.995, 0.50, 0.50], [0.43, 0.43, 0.93, 0.93, 0.93], color="#333", lw=0.8)
    arrow(ax, 0.50, 0.93, 0.50, 0.88)
    label(ax, 0.72, 0.93, "read back at the start of every session")
    ax.text(0.02, 0.29, "Enforced in code, not by instruction", fontsize=8, fontweight="bold")
    box(ax, 0.02, 0.12, 0.30, 0.13, "Phase gates", "records.py check refuses\na run out of phase order", kind="files")
    box(ax, 0.35, 0.12, 0.30, 0.13, "Git hooks", "tests must pass; no credentials;\nno edit to a committed result", kind="files")
    box(ax, 0.68, 0.12, 0.30, 0.13, "Permission tiers", "ask before the holdout, a config\nedit or a download", kind="files")
    ax.set_ylim(0.10, 1.0)
    fig.set_size_inches(6.5, 5.6 * 0.9)
    fig.savefig(OUT / "fig1_architecture.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def fig2():
    fig, ax = canvas(6.5, 6.6)
    legend(ax, 0.985, [("agent", "sub-agent (language model)"), ("harness", "harness (deterministic code)"),
                       ("people", "runner, advisor or human")])
    rows = [
        ("0  Setup", "one time", [("Record the snapshot", "frozen by its manifest", "harness"),
                                   ("Check against the API", "live proof at run start", "harness"),
                                   ("Measure the baseline", "v0 recorded and tagged", "harness")],
         "closes when v0 is tagged, before any candidate exists"),
        ("A  Inventory", "every predictor", [("osap-fetcher", "writes the spec", "agent"), ("field-checker", "fields on the bytes", "agent"),
                                             ("translator", "factor file, preflight", "agent"), ("alpha-reviewer", "audits each batch", "agent")],
         "closes when every predictor has a file or a measured reason  ·  records.py check"),
        ("B  Stage 1", "every constructible", [("Standalone screen", "batches of twelve; raw spread bar", "harness"),
                                               ("factor-evaluator", "checks stamps, writes one row each", "agent")],
         "closes when every constructible predictor has a row  ·  a Stage 2 run before then is refused"),
        ("C  Families", "every passer", [("Assign a family", "by economic definition", "people"),
                                         ("Advisor review", "at the phase boundary", "people"),
                                         ("Declare the order", "by Stage 1 t, written once", "people")],
         "closes when the order is written, before any Stage 2 number exists"),
        ("D  Ratchet", "in declared order", [("Test the next rung", "residual IC t > 2.0\nhedged guard t ≥ −2.0", "harness"),
                                             ("factor-evaluator", "re-derives the verdict", "agent"),
                                             ("Advisor review", "then commit; each\nacceptance is tagged", "people")],
         "closes when every passer has a Stage 2 row  ·  the order is never re-sorted"),
        ("E  Construction", "and the holdout", [("Construction", "Stage 3; β-neutral layer", "harness"),
                                                ("Human approves", "refresh; search finished", "people"),
                                                ("Holdout, once", "read from its cuts", "harness"),
                                                ("The paper", "every row reported", "people")], None)]
    n = len(rows)
    top, rowh, gap = 0.94, 0.105, 0.052
    for i, (ph, sub, steps, closes) in enumerate(rows):
        y = top - i * (rowh + gap) - rowh
        box(ax, 0.02, y, 0.15, rowh, ph, sub, kind="dark", tsize=7.4, ssize=6.3)
        k = len(steps)
        x0, x1 = 0.21, 0.98
        w = (x1 - x0 - 0.025 * (k - 1)) / k
        for j, (t, s, kind) in enumerate(steps):
            xx = x0 + j * (w + 0.025)
            box(ax, xx, y + 0.008, w, rowh - 0.016, t, s, kind=kind, tsize=7.1, ssize=6.2)
            if j < k - 1:
                arrow(ax, xx + w, y + rowh / 2, xx + w + 0.025, y + rowh / 2)
        if i == 4:
            arrow(ax, x0 + 2 * (w + 0.025) + w / 2, y + 0.008, x0 + 2 * (w + 0.025) + w / 2, y - 0.012)
            ax.plot([x0 + 2 * (w + 0.025) + w / 2, x0 + w / 2], [y - 0.012, y - 0.012], color="#333", lw=0.8)
            arrow(ax, x0 + w / 2, y - 0.012, x0 + w / 2, y + 0.008)
            label(ax, x0 + w + 0.12, y - 0.012, "next rung, against the base the last one left")
        if closes:
            yb = y - gap / 2
            ax.plot([0.095, 0.095], [y, y - gap], color="#333", lw=0.8)
            ax.plot([0.07, 0.12], [yb, yb], color="#111", lw=2.2)
            ax.text(0.14, yb - (0.010 if i == 4 else 0), closes, va="center", fontsize=6.3, style="italic", color="#444")
    fig.savefig(OUT / "fig2_phases.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def fig3():
    fig, ax = canvas(6.5, 2.9)
    legend(ax, 0.96, [("agent", "sub-agent (language model)"), ("harness", "harness (deterministic code)"),
                      ("people", "runner, advisor or human")])
    w, h = 0.20, 0.24
    xs = [0.02, 0.27, 0.52, 0.77]
    top = [("1  Read the state", "finish any open\nitem first", "people"), ("2  Declare the batch", "members and stamps\nin the event log", "people"),
           ("3  Run the harness", "ranks, hedges, applies\nthe bars, stamps the result", "harness"),
           ("4  factor-evaluator", "checks the stamps,\nre-derives, writes rows", "agent")]
    for x, (t, s, k) in zip(xs, top):
        box(ax, x, 0.58, w, h, t, s, kind=k)
    for i in range(3):
        arrow(ax, xs[i] + w, 0.70, xs[i + 1], 0.70)
    bot = [("7  Commit and tag", "four stamps in message,\nlocal only; state, reply", "people"),
           ("6  Materialise", "the evaluator adds the\nleg and re-measures", "agent"),
           ("5  Advisor review", "before any acceptance\nis committed", "people")]
    bx = [0.02, 0.27, 0.52]
    for x, (t, s, k) in zip(bx, bot):
        box(ax, x, 0.20, w, h, t, s, kind=k)
    dx, dy = 0.87, 0.32
    ax.add_patch(Polygon([[dx - 0.085, dy], [dx, dy + 0.1], [dx + 0.085, dy], [dx, dy - 0.1]], closed=True, fc="white", ec="#333", lw=0.9))
    ax.text(dx, dy, "accepted?", ha="center", va="center", fontsize=7.4, fontweight="bold")
    arrow(ax, 0.87, 0.58, 0.87, dy + 0.1)
    arrow(ax, dx - 0.085, dy, 0.72, dy); label(ax, 0.75, dy + 0.035, "yes")
    arrow(ax, 0.52, 0.32, 0.47, 0.32)
    arrow(ax, 0.27, 0.32, 0.22, 0.32)
    ax.plot([0.12, 0.12], [0.44, 0.58], color="#333", lw=0.8)
    arrow(ax, 0.12, 0.44, 0.12, 0.58)
    label(ax, 0.17, 0.51, "next turn")
    ax.plot([dx, dx, 0.12], [dy - 0.1, 0.07, 0.07], color="#333", lw=0.8)
    arrow(ax, 0.12, 0.07, 0.12, 0.20)
    label(ax, 0.50, 0.07, "no: the rows are written and the composite is unchanged")
    fig.savefig(OUT / "fig3_cycle.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def fig4():
    vs = bt.VORDER
    B = [bt.VER[v]["baseline"] for v in vs]
    ic = [b["ic"]["ic_mean"] for b in B]
    sh = [b["ls_hedged"]["ls_sharpe"] for b in B]
    dd = [b["ls_hedged"]["ls_maxdd_pct"] for b in B]
    be = [b["beta"]["ls_beta_fullwindow"] for b in B]
    fig, axs = plt.subplots(1, 4, figsize=(7.4, 2.35))
    spec = [(ic, "Mean rank IC", BLUE), (sh, "Long-short Sharpe (hedged)", ORANGE), (dd, "Maximum drawdown, %", GREY),
            (be, "β of the raw long-short", "#6a51a3")]
    x = list(range(len(vs)))
    for a, (y, t, c) in zip(axs, spec):
        a.plot(x, y, "-o", color=c, ms=2.6, lw=1.3)
        a.set_title(t, fontsize=7.6, loc="left")
        a.set_xticks(x)
        a.set_xticklabels(vs, rotation=90, fontsize=6)
        a.tick_params(axis="y", labelsize=6.5)
        a.grid(alpha=0.3, lw=0.5)
    axs[0].annotate(f"{ic[0]:.4f}", (0, ic[0]), textcoords="offset points", xytext=(2, 5), fontsize=6)
    axs[0].annotate(f"{ic[-1]:.4f}", (x[-1], ic[-1]), textcoords="offset points", xytext=(-34, 2), fontsize=6)
    k = max(range(len(sh)), key=lambda i: sh[i])
    axs[1].annotate(f"{vs[k]}  {sh[k]:.3f}", (k, sh[k]), textcoords="offset points", xytext=(-14, 5), fontsize=6)
    axs[1].axhline(sh[0], ls="--", lw=0.7, color="#999")
    axs[1].text(x[-1], sh[0], "v0", fontsize=6, color="#777", va="bottom", ha="right")
    axs[3].axhline(0, lw=0.6, color="#999")
    fig.tight_layout(w_pad=0.6)
    fig.savefig(OUT / "fig4_ratchet.png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def fig5():
    F = bt.FACTS
    n = lambda k: int(F[k][0])
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw={"width_ratios": [1.15, 1]})
    labs = ["OSAP predictors", "constructible, screened", "passed Stage 1", "ratchet-tested", "accepted"]
    vals = [n("n_osap"), n("n_screened"), n("n_s1_pass"), n("n_s2"), n("n_s2_acc")]
    cols = [GREY, BLUE, BLUE, BLUE, ORANGE]
    a.barh(range(5)[::-1], vals, color=cols, height=0.55)
    a.set_yticks(range(5)[::-1]); a.set_yticklabels(labs, fontsize=7)
    for i, v in enumerate(vals):
        a.text(v + 3, 4 - i, str(v), va="center", fontsize=7)
    a.set_title(f"The funnel ({n('n_frontier')} not tested, each with a logged reason)", fontsize=7.6, loc="left")
    a.grid(axis="x", alpha=0.3, lw=0.5)
    blabs = ["Stage 1: NW t of the IC", "Stage 1: IC level", "Stage 2: residual IC bar", "Stage 2: hedged return guard"]
    bv = [n("n_fail_by_t"), int(F["n_s1_fail"][0]) - n("n_fail_by_t"), n("n_s2_rej"), n("n_guard_fail")]
    b.barh(range(4)[::-1], bv, color=[BLUE, BLUE, ORANGE, ORANGE], height=0.55)
    b.set_yticks(range(4)[::-1]); b.set_yticklabels(blabs, fontsize=7)
    for i, v in enumerate(bv):
        b.text(v + 1, 3 - i, str(v), va="center", fontsize=7)
    b.set_title("The bar that decided each rejection", fontsize=7.6, loc="left")
    b.grid(axis="x", alpha=0.3, lw=0.5)
    b.set_xlim(0, max(bv) * 1.12)
    fig.tight_layout(w_pad=1.2)
    fig.savefig(OUT / "fig5_funnel.png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def fig6():
    blk = {b["variant"]: b for b in bt.blocks("056")}["equal_rank_decile"]
    ann = bt.annual_pairs(blk["annual_returns_pct"])
    top = [int(y) for y in bt.b053["ls_top_years"].split(",")]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    ys = [y for y, _ in ann]
    vs = [v for _, v in ann]
    cols = [GREY if y >= 2022 else (ORANGE if y in top else BLUE) for y in ys]
    ax.bar(ys, vs, color=cols, width=0.72)
    ax.axhline(0, color="#333", lw=0.7)
    ax.axvline(2021.5, color="#555", lw=0.8, ls=":")
    ax.text(2021.65, max(vs) * 0.92, "holdout →", fontsize=6.8)
    ax.set_ylabel("D10 − D1 hedged, % per year", fontsize=7)
    ax.set_title("v14 annual hedged long-short (run 056). Orange: the three best in-window years. Grey: the spent "
                 "holdout, 2022–2026:09.", fontsize=7.4, loc="left")
    ax.grid(axis="y", alpha=0.3, lw=0.5)
    ax.set_xticks(range(1999, 2027, 3))
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_annual.png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def fig7():
    d_in = [float(x) for x in bt.b053["decile_avg_ret_pct"].split(",")]
    d_ho = [float(x) for x in bt.b055["decile_avg_ret_pct"].split(",")]
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    x = list(range(10))
    ax.bar([i - 0.19 for i in x], d_in, width=0.38, color=BLUE, label="in-window 1999–2021 (276 months, run 053)")
    ax.bar([i + 0.19 for i in x], d_ho, width=0.38, color=ORANGE, label="holdout 2022-01..2026-09 (57 months, run 055)")
    ax.set_xticks(x); ax.set_xticklabels([f"D{i + 1}" for i in x], fontsize=7)
    ax.set_ylabel("average monthly return, %", fontsize=7)
    ax.set_title("v14 decile average returns: monotone in-window, flat above the bottom decile out of sample",
                 fontsize=7.4, loc="left")
    ax.legend(fontsize=6.6, frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.3, lw=0.5)
    ax.tick_params(labelsize=7)
    ax.axhline(0, color="#333", lw=0.6)
    fig.tight_layout()
    fig.savefig(OUT / "fig7_deciles.png", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        fn()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
