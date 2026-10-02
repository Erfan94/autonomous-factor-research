#!/usr/bin/env python3
"""
Describe the investable universe by period, for the manuscript's Table III (Panel A).

    python3 paper/manuscript/build_sample.py

Read-only and descriptive: it loads the frozen snapshot (DATA_SHA from data/SNAPSHOT_MANIFEST.yaml),
the cached monthly panel, and the harness's own monthly screens (harness.data_layer.build_universe,
membership chain started cold at the first panel month), month by month at each rebalance's signal
date. "Listed" is the same month's cross-section after the absolute screens alone. Nothing is written
outside paper/manuscript/; no stamp moves; no statistic of any factor or composite is computed.
Writes paper/manuscript/sample_universe.json with the stamps it ran on.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.data_layer import (PanelIndex, build_rebalance_schedule, build_universe,  # noqa: E402
                                load_or_build_panel, load_snapshot)
from harness.provenance import all_stamps, load_config, load_runtime, universe_sha  # noqa: E402

PERIODS = [("1999–2004", "1999-01-01", "2004-12-31"), ("2005–2010", "2005-01-01", "2010-12-31"),
           ("2011–2016", "2011-01-01", "2016-12-31"), ("2017–2021", "2017-01-01", "2021-12-31"),
           ("In-window, 1999–2021", "1999-01-01", "2021-12-31"),
           ("Holdout, 2022–2026:09", "2022-01-01", "2026-09-30")]


def listed(pidx, me, cfg):
    """The absolute screens of harness.data_layer.screen_month, without the relative cuts."""
    u = cfg["universe"]
    rows = pidx.month_rows(me)
    df = rows.set_index("ID").join(pidx.meta, how="left")
    df = df[(me - df["date"]) <= pd.Timedelta(days=int(u["max_price_staleness_days"]))]
    df = df[df["exchange"].isin(list(u["exchanges"])) & df["category"].isin(list(u["categories"]))]
    df = df[df["px_unadj"].notna() & (df["px_unadj"] >= float(u["min_price_usd"]))]
    return df[df["mkt_cap_usd"].notna() & df["adv_usd"].notna()]


def main():
    cfg, runtime = load_config(), load_runtime()
    stamps = all_stamps()
    data_sha = stamps["data_sha"]
    snap = load_snapshot(runtime, root=ROOT)
    panel = load_or_build_panel(snap, cfg, runtime, data_sha, root=ROOT)
    pidx = PanelIndex(panel, snap, cfg)
    sched = build_rebalance_schedule("1999-01-01", "2026-09-30")
    monthly = []
    for reb, asof, _, _ in sched:
        uni = build_universe(pidx, asof, cfg)
        lst = listed(pidx, pd.Timestamp(asof), cfg)
        monthly.append(dict(reb=str(reb.date()), asof=str(asof.date()), n=len(uni), ids=list(map(str, uni.index)),
                            median_cap=float(uni["mkt_cap_usd"].median()), total_cap=float(uni["mkt_cap_usd"].sum()),
                            n_listed=len(lst), cap_listed=float(lst["mkt_cap_usd"].sum()),
                            n_nyse=int((uni["exchange"] == "NYSE").sum()), n_nasdaq=int((uni["exchange"] == "NASDAQ").sum())))
    out = []
    for label, a, b in PERIODS:
        ms = [m for m in monthly if a <= m["reb"] <= b]
        ids = set()
        for m in ms:
            ids.update(m["ids"])
        out.append(dict(period=label, months=len(ms),
                        names_mean=sum(m["n"] for m in ms) / len(ms), names_min=min(m["n"] for m in ms),
                        names_max=max(m["n"] for m in ms), distinct=len(ids), firm_months=sum(m["n"] for m in ms),
                        median_cap_bn=sum(m["median_cap"] for m in ms) / len(ms) / 1e9,
                        total_cap_tn=sum(m["total_cap"] for m in ms) / len(ms) / 1e12,
                        pct_listed_names=100 * sum(m["n"] for m in ms) / sum(m["n_listed"] for m in ms),
                        pct_listed_cap=100 * sum(m["total_cap"] for m in ms) / sum(m["cap_listed"] for m in ms),
                        pct_nyse=100 * sum(m["n_nyse"] for m in ms) / sum(m["n"] for m in ms),
                        pct_nasdaq=100 * sum(m["n_nasdaq"] for m in ms) / sum(m["n"] for m in ms)))
    res = dict(script="paper/manuscript/build_sample.py", data_sha=data_sha,
               config_sha=stamps["config_sha"],
               universe_sha=universe_sha(cfg), periods=out)
    (ROOT / "paper/manuscript/sample_universe.json").write_text(json.dumps(res, indent=1) + "\n")
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
