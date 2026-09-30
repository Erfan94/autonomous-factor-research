"""
A tiny synthetic Sharadar snapshot with KNOWN properties, written as parquet
with a manifest, so the data layer and the runner are exercised end to end
against the real schema without any licensed bytes.

Properties the tests rely on (each is asserted by a test, not assumed):
  * N_ALIVE names trade every business day START (1992-01-01) .. END. START
    sits 75 months before the tests' eval_start (1998-06) so a leg with
    history_months = 60 / lookback_months = 75 (a five-year issuance leg) is scorable
    from the first signal date.
  * One name (DELIST_PERF) stops trading on PERF_LAST with no merger action.
  * One name (DELIST_MERGER) stops trading on MERGER_LAST with a `mergerto`
    action three days later.
  * One name (LATE_LISTING) first trades on LATE_START — it must be absent
    from earlier universes and gated out of momentum for 12 months after.
  * One name (PENNY) trades below $1 unadjusted throughout.
  * One name (TINY) has a market cap below the floor.
  * One name (RESTATED) has an SF1 ART row for 1998-12-31 filed 1999-02-15 with
    assets 1000, and a RESTATEMENT of the same period filed 1999-08-01 with
    assets 5000. A signal date in 1999-06 must see 1000.
  * Every alive name has quarterly ART filings, datekey = reportperiod + 45d,
    carrying SF1.marketcap (millions, like DAILY) so a lagged-cap leg reads it.
  * Prices carry a planted signal: names with higher `equity/marketcap` (the
    Value leg) earn higher forward returns, so a Value screen has positive IC.
"""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

START = pd.Timestamp("1992-01-01")
END = pd.Timestamp("2001-12-31")
N_ALIVE = 90

DELIST_PERF = "PERF"
PERF_LAST = pd.Timestamp("1999-09-15")
DELIST_MERGER = "MRGR"
MERGER_LAST = pd.Timestamp("2000-03-10")
LATE_LISTING = "LATE"
LATE_START = pd.Timestamp("1999-07-01")
PENNY = "PENNY"
TINY = "TINY"
RESTATED = "RSTT"

SPECIALS = [DELIST_PERF, DELIST_MERGER, LATE_LISTING, PENNY, TINY, RESTATED]

# Ten more names delist for performance on staggered dates, so the fixture's
# survivorship attrition clears the validator's 5% floor the way a real
# universe does (the BQuant project saw 70% of 1998 names gone by 2025).
EXTRA_DELIST = {f"T{80 + i:03d}": pd.Timestamp("1999-06-01") + pd.DateOffset(months=2 * i)
                for i in range(10)}


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def build(root, seed=0):
    root = Path(root)
    (root / "sharadar").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    bdays = pd.bdate_range(START, END)
    names = [f"T{i:03d}" for i in range(N_ALIVE)] + SPECIALS
    perma = {t: 100000 + i for i, t in enumerate(names)}

    # Static value tilt: a name's book/market ratio is roughly stable and
    # DRIVES its drift, which is the planted signal.
    bm = pd.Series(rng.uniform(0.2, 2.0, len(names)), index=names)
    drift = (bm - bm.mean()) * 0.00025         # per day — a real but not absurd IC
    sep_rows, daily_rows, sf1_rows = [], [], []
    for t in names:
        days = bdays
        if t == LATE_LISTING:
            days = days[days >= LATE_START]
        if t == DELIST_PERF:
            days = days[days <= PERF_LAST]
        if t == DELIST_MERGER:
            days = days[days <= MERGER_LAST]
        if t in EXTRA_DELIST:
            days = days[days <= EXTRA_DELIST[t]]
        n = len(days)
        base = 0.4 if t == PENNY else 30.0
        rets = rng.normal(drift[t], 0.015, n)
        adj = base * np.cumprod(1 + rets)
        unadj = adj.copy()                    # no splits in the fixture
        vol = rng.integers(50_000, 200_000, n) if t != TINY else rng.integers(50_000, 200_000, n)
        sep_rows.append(pd.DataFrame({"ticker": t, "date": days, "open": adj, "high": adj * 1.01,
                                      "low": adj * 0.99, "close": adj, "volume": vol,
                                      "closeadj": adj, "closeunadj": unadj,
                                      "lastupdated": END}))
        # Share counts drift at a per-name rate (-6..+6 %/yr, deterministic, no
        # rng draw so every other stream is unchanged): an issuance leg
        # (marketcap / close over time) must not be a 100% mass point here.
        g = (((perma[t] * 37) % 211) / 210.0 - 0.5) * 0.12
        yrs = np.asarray((days - START).days, dtype=float) / 365.25
        shares0 = 2_000 if t == TINY else 20_000_000
        shares_d = shares0 * (1.0 + g * yrs)
        # Real bulk DAILY.marketcap is in MILLIONS of USD; the fixture matches.
        daily_rows.append(pd.DataFrame({"ticker": t, "date": days, "marketcap": adj * shares_d / 1e6,
                                        "ev": adj * shares_d, "pb": 1.0 / bm[t], "pe": 15.0,
                                        "ps": 2.0, "lastupdated": END}))
        # Quarterly ART rows; equity = bm * marketcap at period end (roughly).
        qends = pd.date_range(START - pd.Timedelta(days=1), END, freq="QE")
        for q in qends:
            if t == LATE_LISTING and q < LATE_START - pd.DateOffset(months=3):
                continue
            if t == DELIST_PERF and q > PERF_LAST:
                continue
            if t == DELIST_MERGER and q > MERGER_LAST:
                continue
            if t in EXTRA_DELIST and q > EXTRA_DELIST[t]:
                continue
            iq = min(max(days.searchsorted(q) - 1, 0), n - 1)
            px_q = adj[iq]
            mc_q = px_q * shares_d[iq]
            eq = bm[t] * mc_q
            assets = eq * 2.5 * (1 + 0.05 * ((q.year - 1996) + q.quarter / 4))
            rev = mc_q * 0.8
            sf1_rows.append({"ticker": t, "dimension": "ART", "calendardate": q,
                             "datekey": q + pd.Timedelta(days=45), "reportperiod": q,
                             "lastupdated": END, "equity": eq, "assets": assets,
                             "marketcap": mc_q / 1e6,
                             "revenue": rev, "cor": rev * 0.6, "sgna": rev * 0.15,
                             "rnd": rev * 0.02, "intexp": rev * 0.01,
                             "netinc": rev * 0.08, "ncfo": rev * 0.1,
                             # Balance-sheet split for a net-operating-assets leg. assets is
                             # proportional to equity here, so the current-asset
                             # and debt shares are made to move with the price
                             # and the ticker: NNCOA then varies name by name and
                             # quarter by quarter (no cross-sectional mass point).
                             "assetsc": assets * (0.2 + 0.5 * (px_q % 7.0) / 7.0),
                             "investmentsnc": 0.0,
                             "liabilities": assets - eq,
                             "debtc": (assets - eq) * (0.05 + 0.1 * (len(t) % 3) / 3),
                             "debtnc": (assets - eq) * (0.1 + 0.4 * (px_q % 11.0) / 11.0)})
    # The restatement: same reportperiod, later datekey, wildly different assets.
    sf1_rows.append({"ticker": RESTATED, "dimension": "ART",
                     "calendardate": pd.Timestamp("1998-12-31"),
                     "datekey": pd.Timestamp("1999-08-01"),
                     "reportperiod": pd.Timestamp("1998-12-31"),
                     "lastupdated": END, "equity": 1.0, "assets": 5000.0, "marketcap": 1.0, "revenue": 1.0,
                     "cor": 0.5, "sgna": 0.1, "rnd": 0.0, "intexp": 0.0,
                     "netinc": 0.1, "ncfo": 0.1,
                     "assetsc": 2000.0, "investmentsnc": 0.0, "liabilities": 4999.0,
                     "debtc": 499.9, "debtnc": 1499.7})
    sf1 = pd.DataFrame(sf1_rows)
    # Pin the original 1998-12-31 filing for RESTATED to assets = 1000.
    m = (sf1["ticker"] == RESTATED) & (sf1["reportperiod"] == pd.Timestamp("1998-12-31")) \
        & (sf1["datekey"] == pd.Timestamp("1999-02-14"))
    sf1.loc[m, "assets"] = 1000.0
    # ARQ rows so the dimension filter is exercised.
    # Every quarterly row also has an ARQ twin with a single-quarter
    # netinccmn that varies by name and quarter (deterministic, no rng draw),
    # so a quarterly-flow ARQ leg is scored here rather than a 100% null; the
    # twenty marker rows (1999-Q1, the filing live at the tests' 1999-06
    # probe date) carry assets = -1 for the dimension-filter test.
    arq_src = sf1[sf1["calendardate"] == pd.Timestamp("1999-03-31")].head(20)
    arq = sf1.assign(dimension="ARQ",
                     netinccmn=sf1["revenue"] / 4.0 * (sf1["assetsc"] / sf1["assets"] - 0.3) * 0.5)
    arq.loc[arq_src.index, "assets"] = -1.0
    sf1 = pd.concat([sf1, arq], ignore_index=True)

    sep = pd.concat(sep_rows, ignore_index=True)
    daily = pd.concat(daily_rows, ignore_index=True)
    tickers = pd.DataFrame({
        "table": "SEP", "permaticker": [perma[t] for t in names], "ticker": names,
        "name": names, "exchange": ["NASDAQ" if i % 2 else "NYSE" for i in range(len(names))],
        "isdelisted": ["Y" if (t in (DELIST_PERF, DELIST_MERGER) or t in EXTRA_DELIST) else "N" for t in names],
        "category": "Domestic Common Stock",
        "siccode": 3000, "sector": [["Technology", "Healthcare", "Industrials"][i % 3] for i in range(len(names))],
        "industry": "Widgets", "firstpricedate": START, "lastpricedate": END,
    })
    tickers = pd.concat([tickers, tickers.assign(table="SF1")], ignore_index=True)
    actions = pd.DataFrame([
        {"date": MERGER_LAST + pd.Timedelta(days=3), "action": "mergerto", "ticker": DELIST_MERGER,
         "name": DELIST_MERGER, "value": np.nan, "contraticker": "T001", "contraname": "T001"},
        {"date": PERF_LAST, "action": "delisted", "ticker": DELIST_PERF, "name": DELIST_PERF,
         "value": np.nan, "contraticker": None, "contraname": None},
        {"date": PERF_LAST, "action": "bankruptcyliquidation", "ticker": DELIST_PERF, "name": DELIST_PERF,
         "value": np.nan, "contraticker": None, "contraname": None},
        {"date": MERGER_LAST + pd.Timedelta(days=3), "action": "delisted", "ticker": DELIST_MERGER,
         "name": DELIST_MERGER, "value": np.nan, "contraticker": None, "contraname": None},
        {"date": pd.Timestamp("1998-05-05"), "action": "regulardividend", "ticker": "T000",
         "name": "T000", "value": 0.1, "contraticker": None, "contraname": None},
    ])
    # A few dividend and event rows so the ACTIONS/EVENTS accessors (HX-3) have
    # something to read: two names that pay, one that stops, one that never does.
    div_rows = []
    for i, t in enumerate(names[:3]):
        for k, d in enumerate(pd.date_range("1998-03-31", periods=6, freq="QE")):
            if t == names[2] and k >= 3:
                continue                       # a payer that stops: DivOmit's shape
            div_rows.append({"date": d, "action": "dividend", "ticker": t, "name": t,
                             "value": 0.05 + 0.01 * i, "contraticker": None, "contraname": None})
    div_rows.append({"date": pd.Timestamp("1999-06-30"), "action": "initiated",
                     "ticker": names[3], "name": names[3], "value": 0.02,
                     "contraticker": None, "contraname": None})
    actions = pd.concat([actions, pd.DataFrame(div_rows)], ignore_index=True)
    events = pd.DataFrame([
        {"ticker": t, "date": d, "eventcodes": code}
        for t, d, code in [(names[0], pd.Timestamp("1998-04-15"), "13|502"),
                           (names[0], pd.Timestamp("1999-02-10"), "202"),
                           (names[1], pd.Timestamp("1998-09-09"), "801"),
                           (names[4], pd.Timestamp("1999-07-01"), "13")]
    ])
    tables = {}
    for name, df in [("SEP", sep), ("SF1", sf1), ("DAILY", daily), ("TICKERS", tickers),
                     ("ACTIONS", actions), ("EVENTS", events)]:
        p = root / "sharadar" / f"{name}.parquet"
        df.to_parquet(p, index=False)
        tables[name] = {"file": p.name, "rows": int(len(df)), "sha256": _sha(p),
                        "columns": list(df.columns)}
    manifest = {"schema_version": 1, "status": "FROZEN", "recorded_on": "2026-01-01T00:00:00Z",
                "source": "synthetic fixture", "tables": tables}
    from harness.provenance import data_sha
    manifest["data_sha"] = data_sha(manifest)
    with open(root / "SNAPSHOT_MANIFEST.yaml", "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return root, manifest, perma
