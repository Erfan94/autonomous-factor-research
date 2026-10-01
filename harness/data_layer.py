"""
The data half of the harness: Sharadar snapshot -> point-in-time monthly panel.

Everything factor-independent lives here, so Stage 1 for factor #40 sees a
byte-identical universe and return series to Stage 1 for factor #1. The
BQuant project got that guarantee from a cache in front of a moving vendor;
this project gets it from a FROZEN snapshot whose per-file sha256 is verified
on open. Nothing here ever fetches from the network.

---------------------------------------------------------------------------
Keys
---------------------------------------------------------------------------
The stock ID is Sharadar's `permaticker`, not the ticker. Tickers are reused
and changed; permaticker is the stable identity. SEP / DAILY / ACTIONS rows
are keyed by ticker and mapped through TICKERS (table == "SEP"); SF1 rows
through TICKERS (table == "SF1"). The mapping must be one-to-one within a
table, and `Snapshot.ticker_map` refuses to build if it is not, because a
ticker that maps to two companies would silently splice their histories.

---------------------------------------------------------------------------
Point-in-time
---------------------------------------------------------------------------
* Universe: rebuilt at every signal date from that date's prices, ADV and
  market cap. A name that delisted in 2008 is in the 2007 universe because the
  screen is applied to 2007 rows, never to today's ticker list.
* Fundamentals: SF1 rows are indexed by `datekey`, the SEC filing date. The
  value used at a signal date is the latest row with datekey <= signal date
  (optionally lagged), within `max_fundamental_age_months`. A restatement
  carries a later datekey and cannot reach an earlier signal.
* Prices: the unadjusted close (`closeunadj`) screens the $1 floor, because
  `close` is split-adjusted and a split in 2020 would otherwise move a 2005
  price below the floor. Returns use `closeadj` (splits AND dividends), so a
  closeadj ratio is a total return.
* Sector: TICKERS.sector is the vendor's CURRENT classification. The screen
  and the Stage 1-3 maths never read it (a diagnostic column there). The
  Phase E construction layer (harness/construction_layer.py) does: its sector
  groups define the neutrality constraint and the risk model's sector
  factors, and it reports how large the Unclassified group is (sector_leak).
"""

import hashlib
import inspect
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from pandas.tseries.offsets import BDay, BMonthEnd

from harness.crosssection import ols_coef

ROOT = Path(__file__).resolve().parent.parent

# Columns the harness itself reads. A factor may read more; preflight checks
# those against the on-disk schema.
#
# SF1's FILING DATE — the point-in-time key — is `date` in the direct Sharadar
# API's schema (verified against api.sharadar.com/v1.0/schema/fundamentals on
# 2026-09-14) and `datekey` in the legacy Nasdaq Data Link export. The harness
# calls it `datekey` throughout and `Snapshot.table` renames `date` -> `datekey`
# on SF1 when only the modern name is present, so both exports load.
REQUIRED_COLUMNS = {
    "SEP": ["ticker", "date", "close", "closeadj", "closeunadj", "volume"],
    "SF1": ["ticker", "dimension", "datekey", "reportperiod"],
    "DAILY": ["ticker", "date", "marketcap"],
    "TICKERS": ["permaticker", "ticker", "exchange", "category", "isdelisted",
                "sector", "industry"],
    "ACTIONS": ["date", "action", "ticker", "value"],
    "EVENTS": ["ticker", "date", "eventcodes"],
}
SF1_FILING_DATE_ALIASES = ("datekey", "date")
# `tickers.table` scopes a row to the price universe or the fundamentals
# universe. Modern values are "stocks" / "fundamentals"; the legacy export used
# "SEP" / "SF1". Both are accepted.
TICKERS_TABLE_COL = "table"
TICKERS_SCOPE = {"SEP": ("stocks", "SEP"), "SF1": ("fundamentals", "SF1")}

PRICE_TABLES = ("SEP", "DAILY", "ACTIONS", "EVENTS")   # keyed like SEP
FUND_TABLES = ("SF1",)


# =============================================================================
# Snapshot: verified, lazy, read-only
# =============================================================================

def sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


class Snapshot:
    """Read-only view over the parquet snapshot described by the manifest.

    `verify_hashes=True` recomputes every listed file's sha256 on open and
    refuses to proceed on a mismatch. It costs seconds on a multi-GB snapshot
    and is what makes DATA_SHA a statement about the bytes a run actually read
    rather than about a file that once had that name.
    """

    def __init__(self, root, manifest, verify_hashes=True):
        self.root = Path(root)
        self.manifest = manifest or {}
        self.tables_meta = self.manifest.get("tables") or {}
        if not self.tables_meta or self.manifest.get("status") == "EMPTY":
            raise RuntimeError(
                "No snapshot is recorded in data/SNAPSHOT_MANIFEST.yaml. Run "
                "`python3 harness/snapshot.py download` (needs the API key in the "
                "environment) then `python3 harness/snapshot.py manifest`.")
        self._frames = {}
        if verify_hashes:
            self.verify()

    def path(self, name):
        meta = self.tables_meta.get(name)
        if not meta:
            raise KeyError(f"table {name} is not in the snapshot manifest")
        return self.root / meta["file"]

    def has(self, name):
        return name in self.tables_meta and self.path(name).exists()

    def verify(self):
        bad = []
        for name, meta in self.tables_meta.items():
            p = self.root / meta["file"]
            if not p.exists():
                bad.append(f"{name}: {p} missing")
                continue
            got = sha256_file(p)
            if got != meta.get("sha256"):
                bad.append(f"{name}: sha256 {got[:12]} != manifest {str(meta.get('sha256'))[:12]}")
        if bad:
            raise RuntimeError("SNAPSHOT DOES NOT MATCH ITS MANIFEST — refusing to run:\n  "
                               + "\n  ".join(bad)
                               + "\nEither restore the files or re-run `snapshot.py manifest` "
                                 "as a deliberate, logged re-baseline (DATA_SHA moves).")

    def table(self, name, columns=None, keep=True):
        """Load a table (cached in memory for the process). `columns=None`
        loads everything the file has. Every datetime column is coerced to
        nanosecond resolution: parquet stores whatever resolution the writer
        used, and pandas refuses to merge_asof across resolutions.
        `keep=False` reads without holding the frame (a one-off build)."""
        key = (name, tuple(columns) if columns else None)
        if key in self._frames:
            return self._frames[key]
        p = self.path(name)
        want = list(columns) if columns else None
        if name == "SF1" and want and "datekey" in want:
            have = self._raw_columns(name)
            if "datekey" not in have and "date" in have:
                want = ["date" if c == "datekey" else c for c in want]
        df = pd.read_parquet(p, columns=want)
        if name == "SF1" and "datekey" not in df.columns and "date" in df.columns:
            df = df.rename(columns={"date": "datekey"})
        for c in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                df[c] = df[c].astype("datetime64[ns]")
        if keep:
            self._frames[key] = df
        return df

    def _raw_columns(self, name):
        import pyarrow.parquet as pq
        return list(pq.ParquetFile(self.path(name)).schema.names)

    def columns(self, name):
        cols = self._raw_columns(name)
        if name == "SF1" and "datekey" not in cols and "date" in cols:
            cols.append("datekey")             # the harness's name for SF1.date
        return cols

    # ---- ticker -> permaticker ------------------------------------------------
    def ticker_map(self, for_table):
        """Series ticker -> ID (permaticker as str), for SEP-keyed or SF1-keyed
        tables. One-to-one or it refuses."""
        t = self.table("TICKERS")
        scope = "SEP" if for_table in PRICE_TABLES else "SF1"
        if TICKERS_TABLE_COL in t.columns:
            sub = t[t[TICKERS_TABLE_COL].isin(TICKERS_SCOPE[scope])]
            if sub.empty:                      # synthetic or single-table fixture
                sub = t
        else:
            sub = t
        sub = sub.dropna(subset=["ticker", "permaticker"])
        dup = sub.groupby("ticker")["permaticker"].nunique()
        dup = dup[dup > 1]
        if len(dup):
            raise RuntimeError(
                f"TICKERS[{scope}] maps {len(dup)} tickers to more than one "
                f"permaticker (e.g. {list(dup.index[:5])}). A ticker that names "
                "two companies would splice their histories. Resolve by date "
                "before using this snapshot; the harness will not guess.")
        m = sub.drop_duplicates("ticker").set_index("ticker")["permaticker"]
        return m.astype("int64").astype(str)

    def ticker_meta(self):
        """Per-ID static columns: exchange, category, sector, industry,
        isdelisted. SEP-scope rows; one row per ID."""
        t = self.table("TICKERS")
        if TICKERS_TABLE_COL in t.columns and t[TICKERS_TABLE_COL].isin(TICKERS_SCOPE["SEP"]).any():
            t = t[t[TICKERS_TABLE_COL].isin(TICKERS_SCOPE["SEP"])]
        cols = [c for c in ["permaticker", "ticker", "exchange", "category", "isdelisted",
                            "sector", "industry", "siccode", "lastpricedate",
                            "firstpricedate"] if c in t.columns]
        t = t[cols].dropna(subset=["permaticker"]).drop_duplicates("permaticker")
        t = t.assign(ID=t["permaticker"].astype("int64").astype(str)).set_index("ID")
        return t.drop(columns=["permaticker"])


def load_snapshot(runtime, root=ROOT, verify_hashes=True):
    manifest_path = Path(root) / runtime["data"]["manifest"]
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f) or {}
    return Snapshot(Path(root) / runtime["data"]["root"], manifest, verify_hashes)


# =============================================================================
# Calendar
# =============================================================================

def _first_bday_of_month(ts):
    cal_ms = ts.replace(day=1)
    return pd.date_range(cal_ms, cal_ms + pd.Timedelta(days=7), freq="B")[0].normalize()


def build_rebalance_schedule(eval_start, eval_end):
    """[(rebalance_date, signal_asof, ret_start, ret_end), ...] — the BQuant
    project's schedule, unchanged.

    The signal is observed at the business month-end BEFORE the rebalance date,
    and the return is earned over the month FOLLOWING it. `eval_end` is a hard
    wall: the final month's return window is clipped to it, so the reserved
    out-of-sample period cannot be entered even partially.
    """
    start_ts = pd.to_datetime(eval_start).normalize()
    end_ts = pd.to_datetime(eval_end).normalize()
    rebs = list(pd.date_range(_first_bday_of_month(start_ts), end_ts, freq="BMS"))
    rebs_plus = rebs + [pd.to_datetime(rebs[-1] + pd.offsets.BMonthBegin(1)).normalize()]
    schedule = []
    for i, reb_dt in enumerate(rebs):
        reb_dt = pd.to_datetime(reb_dt).normalize()
        next_reb = pd.to_datetime(rebs_plus[i + 1]).normalize()
        signal_asof = (reb_dt - BMonthEnd(1)).normalize()
        ret_start = max(start_ts, reb_dt)
        ret_end = min(end_ts, (next_reb - BDay(1)).normalize())
        if ret_start > ret_end:
            continue
        schedule.append((reb_dt, signal_asof, ret_start, ret_end))
    return schedule


def last_completed_month_end(today=None):
    """Last day of the previous calendar month. A partial month's return is not
    a month's return."""
    today = pd.Timestamp(today) if today is not None else pd.Timestamp.today()
    return (today.replace(day=1) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")


def to_bme(dates):
    """Map each date to its business month-end. Vectorised through the unique
    calendar month-ends, so it is cheap on 15M rows."""
    d = pd.to_datetime(pd.Series(dates))
    cal_me = d.dt.to_period("M").dt.to_timestamp("M")
    uniq = pd.Series(cal_me.unique())
    bme = uniq + BMonthEnd(0)
    # BMonthEnd(0) on a weekend calendar month-end rolls FORWARD in pandas; roll
    # back instead so the business month-end never lands in the next month.
    over = bme.dt.to_period("M") != uniq.dt.to_period("M")
    bme[over] = uniq[over] - BMonthEnd(1)
    m = dict(zip(uniq, bme))
    return cal_me.map(m)


# =============================================================================
# Monthly panel — built once per snapshot, cached on disk
# =============================================================================

def panel_cache_key(data_sha, cfg):
    u = cfg["universe"]
    return hashlib.sha256(
        f"{data_sha}|{u['adv_lookback_days']}|{u['adv_min_days']}|"
        f"{u.get('daily_marketcap_scale', 1)}|panel-v2".encode()
    ).hexdigest()[:12]


def build_monthly_panel(snap, cfg, log=print):
    """One row per (ID, business month-end) with the last trade of the month.

    Columns: ID, me, date (last trade date), px_unadj, closeadj, volume,
    adv_usd (median close*volume over the trailing window), mkt_cap_usd (last
    DAILY.marketcap in the month), n_days_in_month.
    """
    u = cfg["universe"]
    t0 = time.time()
    sep = snap.table("SEP", REQUIRED_COLUMNS["SEP"]).copy()
    sep["date"] = pd.to_datetime(sep["date"])
    tmap = snap.ticker_map("SEP")
    sep["ID"] = sep["ticker"].map(tmap)
    unmapped = sep["ID"].isna().mean()
    sep = sep.dropna(subset=["ID"])
    sep = sep.sort_values(["ID", "date"], kind="mergesort").reset_index(drop=True)
    log(f"    SEP: {len(sep):,} rows, {sep['ID'].nunique():,} IDs "
        f"({unmapped * 100:.2f}% rows without a permaticker, dropped)")

    # `close` is split-adjusted; close*volume is split-invariant when volume is
    # adjusted the same way (it is), so ADV is fine on it. The $1 floor is not.
    sep["dv"] = sep["close"].astype(float) * sep["volume"].astype(float)
    roll = (sep.groupby("ID")["dv"]
               .rolling(int(u["adv_lookback_days"]), min_periods=int(u["adv_min_days"]))
               .median())
    sep["adv_usd"] = roll.reset_index(level=0, drop=True)
    sep["me"] = to_bme(sep["date"]).values
    sep["n_days_in_month"] = sep.groupby(["ID", "me"])["date"].transform("count")
    last = sep.groupby(["ID", "me"], sort=False).tail(1)
    last = last.rename(columns={"closeunadj": "px_unadj"})
    panel = last[["ID", "me", "date", "px_unadj", "closeadj", "volume", "adv_usd",
                  "n_days_in_month"]].copy()
    del sep

    daily = snap.table("DAILY", REQUIRED_COLUMNS["DAILY"]).copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["ID"] = daily["ticker"].map(tmap)
    daily = daily.dropna(subset=["ID"]).sort_values(["ID", "date"], kind="mergesort")
    daily["me"] = to_bme(daily["date"]).values
    dlast = (daily.groupby(["ID", "me"], sort=False).tail(1)
                  [["ID", "me", "marketcap"]]
                  .rename(columns={"marketcap": "mkt_cap_usd"}))
    # Bulk DAILY.marketcap is in millions of USD; the screen is in raw USD.
    dlast["mkt_cap_usd"] = dlast["mkt_cap_usd"].astype(float) * float(u.get("daily_marketcap_scale", 1))
    del daily
    panel = panel.merge(dlast, on=["ID", "me"], how="left")
    panel = panel.sort_values(["ID", "me"], kind="mergesort").reset_index(drop=True)
    log(f"    monthly panel: {len(panel):,} ID-months in {time.time() - t0:.0f}s")
    return panel


def load_or_build_panel(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = panel_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"monthly_panel_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    monthly panel: cache hit {p.name}")
        return pd.read_parquet(p)
    panel = build_monthly_panel(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        panel.to_parquet(p, index=False)
        log(f"    monthly panel: cached as {p.name}")
    return panel


# =============================================================================
# First trade of each month — the skip-a-day return base (diagnostic only)
# =============================================================================
#
# `--return-start skip1` (run_test.py, `--baseline --stage 2` only) moves the
# base of month t+1's forward return from the signal-date close to the close
# of the name's FIRST trade in month t+1. That needs one SEP row per
# (ID, business month-end) the monthly panel does not carry (it holds the
# LAST trade). It is built separately, and only when the flag is set, so the
# panel, its cache key and every default-path number are untouched.

RETURN_START_MODES = ("close", "skip1")


def first_trade_cache_key(data_sha):
    return hashlib.sha256(f"{data_sha}|first-trade-v1".encode()).hexdigest()[:12]


def build_first_trade_monthly(snap, log=print):
    """One row per (ID, business month-end): the FIRST SEP trade of the
    calendar month. Columns: ID, me, first_date, first_closeadj."""
    t0 = time.time()
    tmap = snap.ticker_map("SEP")
    sep = snap.table("SEP", ["ticker", "date", "closeadj"], keep=False)
    sep = sep.assign(ID=sep["ticker"].map(tmap)).dropna(subset=["ID"])
    sep["date"] = pd.to_datetime(sep["date"])
    sep = sep.sort_values(["ID", "date"], kind="mergesort").reset_index(drop=True)
    sep["me"] = to_bme(sep["date"]).values
    first = sep.groupby(["ID", "me"], sort=False).head(1)
    out = (first[["ID", "me", "date", "closeadj"]]
           .rename(columns={"date": "first_date", "closeadj": "first_closeadj"})
           .reset_index(drop=True))
    del sep
    log(f"    first-trade monthly: {len(out):,} ID-months in {time.time() - t0:.0f}s")
    return out


def load_or_build_first_trade(snap, runtime, data_sha, root=ROOT, log=print):
    key = first_trade_cache_key(data_sha)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"first_trade_monthly_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    first-trade monthly: cache hit {p.name}")
        return pd.read_parquet(p)
    out = build_first_trade_monthly(snap, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        out.to_parquet(p, index=False)
        log(f"    first-trade monthly: cached as {p.name}")
    return out


# =============================================================================
# Daily value-weighted market return — built once per snapshot, cached on disk
# =============================================================================
#
# OSAP's `mktrf` (CRSP VW market, from Ken French) feeds betas, coskewness,
# price-delay regressions, idiosyncratic volatility and announcement returns.
# Sharadar holds no index series, so the harness builds the CRSP-like analogue
# from the snapshot itself:
#
#   * Constituents: SEP-scope TICKERS whose category is in
#     universe.categories and exchange in universe.exchanges (the same static,
#     CURRENT TICKERS classification the universe screen reads). NO price,
#     size or ADV screen — CRSP's VW market has none, and the value weights
#     already make microcaps immaterial.
#   * Trading calendar: a date is a market trading day only if at least
#     MARKET_MIN_DAY_FRAC (half) of the trailing MARKET_CAL_WINDOW-date median
#     number of constituents printed on it. A stray holiday/weekend row for a
#     few names is NOT a trading day and its rows are discarded; otherwise it
#     would become every other name's "prior day" and empty the next day.
#     Every kept day must then carry >= MARKET_MIN_NAMES names or the build
#     raises.
#   * r_{i,d} = closeadj_d / closeadj_{d-1} - 1, a total return. d-1 is the
#     PREVIOUS MARKET TRADING DAY, so a name enters day d only if it printed
#     on both d-1 and d.
#   * w_{i,d-1} = DAILY.marketcap on d-1. mkt_d = sum(w r) / sum(w) over names
#     with both.
#   * NOT CRSP: (a) returns across a trading gap (a name missing on d-1) are
#     excluded, where CRSP books them on the day trading resumes; (b) there
#     are NO DELISTING RETURNS — a name's final move off the exchange is not
#     in the series, where CRSP VW includes DLRET. Both are small for a
#     value-weighted index; a factor using this series declares them.
#   * Coverage: DAILY.marketcap starts 1998-12-01 in the snapshot, so the
#     series starts 1998-12-02. That is a data limit, not a build choice; a
#     factor needing N days of history sets `min_days` in market_daily.
#   * Bad-print guards; nothing else is trimmed or winsorised:
#     - SPIKE (causal): a name-day with r_d > MARKET_SPIKE_UP (+100%) or
#       r_d < MARKET_SPIKE_DOWN (-80%) is an extreme print on its own and is
#       dropped for that name. Day d is judged on r_d alone — nothing after d
#       is read, so the market value on any date is unchanged when later rows
#       are deleted (tested). This replaced a pair rule that read r_{d+1} to
#       clean day d (a one-day look-ahead into the holding month when d is
#       the signal day). A genuine >+100% day is also dropped; at value
#       weights that costs little, and CRSP-VW keeps it — declared.
#     - REVERSAL (causal): day d is dropped when day d-1 (the previous
#       trading day, same name) was dropped as a spike and r_d reverses it:
#       (r_{d-1} > +100% and r_d < -50%) or (r_{d-1} < -80% and r_d > +400%),
#       with |(1+r_{d-1})(1+r_d) - 1| <= MARKET_PAIR_NET_TOL (50%). Reads
#       only d-1 and d.
#     - RETURN: any other name-day with |r| > MARKET_MAX_ABS_RET (500%).
#     - WEIGHT: w_{i,d-1} is dropped when the cap exceeds MARKET_MAX_CAP_TO_ADV
#       (1e5) times the name's median daily dollar volume (close*volume) over
#       its MARKET_ADV_ROWS (20) SEP rows ending d-1 — a daily turnover below
#       0.001%, which no genuinely large company has. Point-in-time (reads
#       nothing after d-1). Measured on DATA_SHA 1c9ce79dd5a5: DAILY.marketcap
#       carries vendor errors with no printed-return symptom — ISWI at
#       $1.3-4.2 TRILLION for 21 days in Jan-Feb 2000 (8e11 implied shares)
#       made 2000-02-10 a +10.2% market day on its own; WHRT (1998) and RPTP
#       (2004) are the same shape, plus bankrupt shells with $50B+ caps. Among
#       genuine names with >0.3% weight the 99.9th pct cap/ADV is ~6.6e3; the
#       three errors sit at 5e7-8e7. The guard also drops untraded shells
#       (zero median volume); they drop ~3% of name-days but ~0.17% of weight.
#   * `ew_ret` (the equal-weighted mean of the same name-days) and `n_names`
#     are kept as diagnostics.
#
# It is a RAW market return, NOT an excess return: the snapshot holds no
# risk-free rate. Over daily windows rf is a near-constant ~0-2 bp/day, which
# does not move a beta, a covariance or a regression residual materially, but
# it does shift an intercept, and a factor that uses this series in place of
# mktrf must say so in its docstring (the declared deviation).

MARKET_MAX_ABS_RET = 5.0
MARKET_SPIKE_UP = 1.0              # r_d > +100%: an extreme print on its own
MARKET_SPIKE_DOWN = -0.8           # r_d < -80%: an extreme print on its own
MARKET_REV_AFTER_UP = -0.5         # after an up-spike, r_d < -50% reverses it
MARKET_REV_AFTER_DOWN = 4.0        # after a down-spike, r_d > +400% reverses it
MARKET_PAIR_NET_TOL = 0.5
MARKET_MAX_CAP_TO_ADV = 1e5
MARKET_ADV_ROWS = 20
MARKET_CAL_WINDOW = 21
MARKET_MIN_DAY_FRAC = 0.5
MARKET_MIN_NAMES = 30
MARKET_VERSION = "mkt-v4"
MARKET_START_NOTE = "1998-12-02"   # DAILY.marketcap starts 1998-12-01 (data limit)


def _market_builder_sha():
    """Hash of the builder's source and constants, so a code change can never
    be served a parquet built by the previous code."""
    src = "".join(inspect.getsource(f) for f in
                  (market_constituent_ids, market_trading_calendar, build_market_daily))
    consts = (MARKET_MAX_ABS_RET, MARKET_SPIKE_UP, MARKET_SPIKE_DOWN, MARKET_REV_AFTER_UP,
              MARKET_REV_AFTER_DOWN, MARKET_PAIR_NET_TOL,
              MARKET_MAX_CAP_TO_ADV, MARKET_ADV_ROWS, MARKET_CAL_WINDOW,
              MARKET_MIN_DAY_FRAC, MARKET_MIN_NAMES, MARKET_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def market_cache_key(data_sha, cfg):
    u = cfg["universe"]
    return hashlib.sha256(
        f"{data_sha}|{sorted(u['exchanges'])}|{sorted(u['categories'])}|"
        f"{u.get('daily_marketcap_scale', 1)}|{_market_builder_sha()}".encode()
    ).hexdigest()[:12]


# SURVIVORSHIP OF THE ID FILTER (a comment OUTSIDE the function, so the
# market / ps / trend builder hashes do not move). The filter reads TODAY's
# TICKERS.exchange; the ps and trend builders then apply the exchange IN FORCE
# (ps_exchange_asof, PS_EXCHANGE_RULE "retro") only to the ids this returns.
# Sharadar keeps a delisted name's LAST LISTED exchange in TICKERS (of 1,081 common-stock
# SEP names whose last ACTIONS move is to OTC, 1,077 still read NASDAQ / NYSE /
# NYSEMKT), so the gap is only the 17 common-stock SEP names whose current
# exchange is OTC / BATS / NYSEARCA / null, of which FNMA, FMCC (NYSE -> OTC
# 2010-07-08), CBOE (NASDAQ -> BATS 2018-09-17) and EVEIQ (NYSEMKT -> NYSEARCA
# 2006-09-29) carry an ACTIONS move out of a listed exchange. Measured on
# DATA_SHA 52402f7d1f9c, 1999-2022, by rebuilding with every common-stock id:
# trend fit(m) name-months lost <= 0.073% in any year (2005: 24 of 32,691;
# 222 in all), the NYSE 10th-percentile cut moved <= 0.36% (2009); PS eligible
# name-months lost <= 0.11% (2004: 24 of 21,720; 123 in all, FNMA/FMCC/EVEIQ),
# <= 0.90% of the eligible cap m_t (2001). Below the review's 0.5% / 1% bars,
# so the filter stays. Alpha-review 2026-09-25.
def market_constituent_ids(snap, cfg):
    """IDs in the CRSP-like all-stock market: common-stock category on a
    listed exchange, per the universe config. No other screen."""
    u = cfg["universe"]
    meta = snap.ticker_meta()
    keep = pd.Series(True, index=meta.index)
    if "exchange" in meta.columns:
        keep &= meta["exchange"].isin(list(u["exchanges"]))
    if "category" in meta.columns:
        keep &= meta["category"].isin(list(u["categories"]))
    return set(meta.index[keep])


def market_trading_calendar(dates):
    """Sorted trading days from the constituents' print dates: a date counts
    only if its print count is >= MARKET_MIN_DAY_FRAC x the median count over
    the trailing MARKET_CAL_WINDOW dates (itself included)."""
    cnt = pd.Series(dates).value_counts().sort_index()
    med = cnt.rolling(MARKET_CAL_WINDOW, min_periods=1).median()
    return pd.DatetimeIndex(cnt.index[cnt >= MARKET_MIN_DAY_FRAC * med])


def build_market_daily(snap, cfg, log=print):
    """Frame indexed by date: mkt_ret (prior-day-cap-weighted), ew_ret,
    n_names. See the block comment above for every rule."""
    t0 = time.time()
    ids = market_constituent_ids(snap, cfg)
    tmap = snap.ticker_map("SEP")
    tmap = tmap[tmap.isin(ids)]

    sep = snap.table("SEP", ["ticker", "date", "closeadj", "close", "volume"], keep=False)
    sep = sep.assign(ID=sep["ticker"].map(tmap)).dropna(subset=["ID"])
    sep = sep.assign(dv=sep["close"].astype(float) * sep["volume"].astype(float))
    sep = sep[["ID", "date", "closeadj", "dv"]]
    daily = snap.table("DAILY", ["ticker", "date", "marketcap"], keep=False)
    daily = daily.assign(ID=daily["ticker"].map(tmap)).dropna(subset=["ID"])
    daily = daily[["ID", "date", "marketcap"]].drop_duplicates(["ID", "date"], keep="last")

    df = (sep.drop_duplicates(["ID", "date"], keep="last")
             .merge(daily, on=["ID", "date"], how="left")
             .sort_values(["ID", "date"], kind="mergesort")
             .reset_index(drop=True))
    del sep, daily
    cal = market_trading_calendar(df["date"])
    n_stray = int((~df["date"].isin(cal)).sum())
    df = df[df["date"].isin(cal)].reset_index(drop=True)
    prev_mkt_day = pd.Series(cal[:-1], index=cal[1:])

    adv = (df.groupby("ID", sort=False)["dv"]
             .rolling(MARKET_ADV_ROWS, min_periods=1).median()
             .reset_index(level=0, drop=True)
             .reindex(df.index))
    cap_usd = df["marketcap"].to_numpy(dtype=float) * float(cfg["universe"].get("daily_marketcap_scale", 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        plausible = cap_usd <= MARKET_MAX_CAP_TO_ADV * adv.to_numpy(dtype=float)
    same = df["ID"].to_numpy()[1:] == df["ID"].to_numpy()[:-1]
    p_prev = np.r_[np.nan, np.where(same, df["closeadj"].to_numpy()[:-1], np.nan)]
    w_prev = np.r_[np.nan, np.where(same, df["marketcap"].to_numpy(dtype=float)[:-1], np.nan)]
    ok_w_prev = np.r_[False, same & plausible[:-1]]
    d_prev = np.r_[np.datetime64("NaT"), np.where(same, df["date"].to_numpy()[:-1],
                                                  np.datetime64("NaT"))].astype("datetime64[ns]")
    r = df["closeadj"].to_numpy(dtype=float) / p_prev - 1.0
    want_prev = prev_mkt_day.reindex(df["date"]).to_numpy()
    valid_r = (d_prev == want_prev) & np.isfinite(r)
    # Causal bad-print guards: day d is judged on r_d and r_{d-1} only.
    with np.errstate(invalid="ignore"):
        spike_up = valid_r & (r > MARKET_SPIKE_UP)
        spike_dn = valid_r & (r < MARKET_SPIKE_DOWN)
        spike = spike_up | spike_dn
        # valid_r[j] means row j-1 is the same name on the previous trading day.
        prev_up = np.r_[False, spike_up[:-1]] & valid_r
        prev_dn = np.r_[False, spike_dn[:-1]] & valid_r
        r_prev = np.r_[np.nan, r[:-1]]
        net = np.abs((1.0 + r_prev) * (1.0 + r) - 1.0) <= MARKET_PAIR_NET_TOL
        reversal = ((prev_up & (r < MARKET_REV_AFTER_UP)) |
                    (prev_dn & (r > MARKET_REV_AFTER_DOWN))) & net & ~spike
    drop = spike | reversal
    base = valid_r & np.isfinite(w_prev) & (w_prev > 0)
    ok = base & ~drop & (np.abs(r) <= MARKET_MAX_ABS_RET) & ok_w_prev
    n_spike = int(spike.sum())
    n_rev = int(reversal.sum())
    n_bad = int((base & ~drop & (np.abs(r) > MARKET_MAX_ABS_RET)).sum())
    n_badw = int((base & ~ok_w_prev).sum())
    x = pd.DataFrame({"date": df["date"].to_numpy()[ok], "r": r[ok], "w": w_prev[ok]})
    del df
    x["wr"] = x["w"] * x["r"]
    g = x.groupby("date", sort=True)
    out = pd.DataFrame({"mkt_ret": g["wr"].sum() / g["w"].sum(),
                        "ew_ret": g["r"].mean(),
                        "n_names": g["r"].size().astype("int64")})
    out.index.name = "date"
    thin = out[out["n_names"] < MARKET_MIN_NAMES]
    if len(thin):
        raise RuntimeError(
            f"market daily: {len(thin)} trading day(s) with fewer than {MARKET_MIN_NAMES} "
            f"names (e.g. {thin.index[0].date()}: {int(thin['n_names'].iloc[0])}). The "
            "calendar or a guard is wrong; the harness will not serve a thin market.")
    out.attrs = {"n_spike": n_spike, "n_reversal": n_rev, "n_bad_ret": n_bad, "n_bad_weight": n_badw,
                 "n_stray_rows": n_stray}
    log(f"    market daily: {len(out):,} days, {len(x):,} name-days from {len(ids):,} "
        f"constituent IDs; dropped {n_stray} stray-date rows, {n_spike} spike and {n_rev} "
        f"reversal name-days, {n_bad} other returns |r| > {MARKET_MAX_ABS_RET:g}, {n_badw:,} weights "
        f"cap > {MARKET_MAX_CAP_TO_ADV:g} x ADV; {time.time() - t0:.0f}s")
    return out


def load_or_build_market(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = market_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"market_daily_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    market daily: cache hit {p.name}")
        return pd.read_parquet(p)
    mkt = build_market_daily(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        mkt.to_parquet(p)
        log(f"    market daily: cached as {p.name}")
    return mkt


# =============================================================================
# Daily Fama-French three factors (mkt, SMB, HML) — built once, cached on disk
# =============================================================================
#
# OSAP's daily regressions on the FF3 model (idiosyncratic volatility,
# FF3 residual momentum / reversal, ...) read Ken French's daily factors.
# Sharadar holds none, so the harness builds the analogue from the snapshot,
# on the SAME name-days as the market series above:
#
#   * Constituents, trading calendar, returns, prior-day weights and every
#     bad-print guard (stray dates, causal spike / reversal, |r| > 500%, cap >
#     1e5 x ADV) are the market builder's, rule for rule: `_ff3_name_days`
#     repeats build_market_daily's row logic (that function is left untouched
#     so the market series and its cache key cannot move), and a test pins
#     that the all-name value-weighted mean of these name-days IS
#     build_market_daily's mkt_ret, exactly. `mkt` here is that series.
#   * Formation (Fama-French 1993): at each June business month-end F_y,
#     eligible = constituents with a positive, plausible (cap <= 1e5 x ADV)
#     DAILY.marketcap on their last June row within FF3_ME_TOL_DAYS of F_y
#     (ME_June) AND on their last December y-1 row within FF3_ME_TOL_DAYS of
#     that December's business month-end (ME_Dec), AND positive book equity.
#     Size: S if ME_June <= the median ME_June of ELIGIBLE NYSE names, else B.
#     B/M = BE / ME_Dec: L if <= the eligible-NYSE 30th percentile, M if <=
#     the 70th, else H (pandas linear quantiles; ties go to the lower bucket,
#     the WRDS replication's convention). The breakpoint exchange is
#     universe.size_breakpoint.exchange ("NYSE").
#   * Book equity (BMdec's convention, the project's FF-style BE): from SF1
#     dimension ARY (annual, as reported), the fiscal year whose reportperiod
#     falls in calendar y-1, the latest such filing with datekey <= F_y
#     (POINT-IN-TIME: a 10-K filed after the June formation date is not used
#     that year, and a restatement filed later cannot reach it).
#     SE = equity, or assets - liabilities when equity is missing;
#     BE = SE + taxliabilities (NaN -> 0); preferred stock = 0.
#   * Holding: the June-y assignment applies to every market day d with
#     F_y < d <= F_{y+1} (the first July day's return runs from the June-end
#     close). Six portfolios, value-weighted DAILY with the PRIOR trading
#     day's cap (the market's weights). SMB = mean(SL, SM, SH) - mean(BL, BM,
#     BH); HML = mean(SH, BH) - mean(SL, BL).
#
# DEVIATIONS from Ken French's construction (a factor using this declares
# them): (a) NO RISK-FREE RATE is held — mkt is the RAW value-weighted return,
# not Mkt-RF; SMB and HML are long-short, so rf cancels in them. (b) TICKERS
# exchange / category are CURRENT classifications (a firm that moved from
# NASDAQ to NYSE in 2010 counts as NYSE for the 1999 breakpoints). (c) Book
# equity: SF1 has no seq/ceq split, no txditc (taxliabilities is total tax
# liabilities, an approximation) and no preferred stock, so PS = 0. (d) No
# two-years-in-Compustat requirement. (e) ME is per permaticker (no CRSP
# permco roll-up of share classes). (f) No delisting returns and no returns
# across a trading gap, as for the market series. (g) Coverage: DAILY.marketcap
# starts 1998-12-01, so the first formation is June 1999 (needs Dec 1998
# ME); smb / hml are NaN before the first July 1999 trading day while mkt runs
# from 1998-12-02. `MonthContext.ff3_daily` serves only complete rows.
#
# Every day inside a holding year must have >= FF3_MIN_PORT_NAMES names in
# each of the six portfolios, and every formation must have >=
# FF3_MIN_BREAKPOINT_NAMES eligible NYSE names, or the build raises: the
# harness will not serve a thin factor.

FF3_FORMATION_MONTH = 6
FF3_SIZE_PCTL = 0.5
FF3_BM_PCTLS = (0.3, 0.7)
FF3_BE_DIMENSION = "ARY"
FF3_ME_TOL_DAYS = 7
FF3_MIN_BREAKPOINT_NAMES = 20
FF3_MIN_PORT_NAMES = 5
FF3_PORTS = ("SL", "SM", "SH", "BL", "BM", "BH")
FF3_VERSION = "ff3-v1"
FF3_BE_COLUMNS = ["ticker", "dimension", "datekey", "reportperiod",
                  "equity", "assets", "liabilities", "taxliabilities"]


def ff3_formation_date(year):
    """The business month-end of FF3_FORMATION_MONTH (June) in `year`."""
    me = pd.Timestamp(year=int(year), month=FF3_FORMATION_MONTH, day=1) + pd.offsets.MonthEnd(0)
    return to_bme([me]).iloc[0]


def _ff3_name_days(snap, cfg):
    """Every constituent row on the market trading calendar, with the market
    builder's return, prior-day weight and guards. Frame: ID, date, r, w
    (prior-day DAILY.marketcap), ok (the name-day enters a value-weighted
    mean), cap_usd (same-day cap in USD) and plausible (cap <= 1e5 x the
    trailing 20-row median dollar volume, the market's weight guard applied
    to the same-day cap). Sorted by ID, date. The row logic is
    build_market_daily's, line for line; see the block comment above."""
    ids = market_constituent_ids(snap, cfg)
    tmap = snap.ticker_map("SEP")
    tmap = tmap[tmap.isin(ids)]

    sep = snap.table("SEP", ["ticker", "date", "closeadj", "close", "volume"], keep=False)
    sep = sep.assign(ID=sep["ticker"].map(tmap)).dropna(subset=["ID"])
    sep = sep.assign(dv=sep["close"].astype(float) * sep["volume"].astype(float))
    sep = sep[["ID", "date", "closeadj", "dv"]]
    daily = snap.table("DAILY", ["ticker", "date", "marketcap"], keep=False)
    daily = daily.assign(ID=daily["ticker"].map(tmap)).dropna(subset=["ID"])
    daily = daily[["ID", "date", "marketcap"]].drop_duplicates(["ID", "date"], keep="last")

    df = (sep.drop_duplicates(["ID", "date"], keep="last")
             .merge(daily, on=["ID", "date"], how="left")
             .sort_values(["ID", "date"], kind="mergesort")
             .reset_index(drop=True))
    del sep, daily
    cal = market_trading_calendar(df["date"])
    n_stray = int((~df["date"].isin(cal)).sum())
    df = df[df["date"].isin(cal)].reset_index(drop=True)
    prev_mkt_day = pd.Series(cal[:-1], index=cal[1:])

    adv = (df.groupby("ID", sort=False)["dv"]
             .rolling(MARKET_ADV_ROWS, min_periods=1).median()
             .reset_index(level=0, drop=True)
             .reindex(df.index))
    cap_usd = df["marketcap"].to_numpy(dtype=float) * float(cfg["universe"].get("daily_marketcap_scale", 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        plausible = cap_usd <= MARKET_MAX_CAP_TO_ADV * adv.to_numpy(dtype=float)
    same = df["ID"].to_numpy()[1:] == df["ID"].to_numpy()[:-1]
    p_prev = np.r_[np.nan, np.where(same, df["closeadj"].to_numpy()[:-1], np.nan)]
    w_prev = np.r_[np.nan, np.where(same, df["marketcap"].to_numpy(dtype=float)[:-1], np.nan)]
    ok_w_prev = np.r_[False, same & plausible[:-1]]
    d_prev = np.r_[np.datetime64("NaT"), np.where(same, df["date"].to_numpy()[:-1],
                                                  np.datetime64("NaT"))].astype("datetime64[ns]")
    r = df["closeadj"].to_numpy(dtype=float) / p_prev - 1.0
    want_prev = prev_mkt_day.reindex(df["date"]).to_numpy()
    valid_r = (d_prev == want_prev) & np.isfinite(r)
    with np.errstate(invalid="ignore"):
        spike_up = valid_r & (r > MARKET_SPIKE_UP)
        spike_dn = valid_r & (r < MARKET_SPIKE_DOWN)
        spike = spike_up | spike_dn
        prev_up = np.r_[False, spike_up[:-1]] & valid_r
        prev_dn = np.r_[False, spike_dn[:-1]] & valid_r
        r_prev = np.r_[np.nan, r[:-1]]
        net = np.abs((1.0 + r_prev) * (1.0 + r) - 1.0) <= MARKET_PAIR_NET_TOL
        reversal = ((prev_up & (r < MARKET_REV_AFTER_UP)) |
                    (prev_dn & (r > MARKET_REV_AFTER_DOWN))) & net & ~spike
    drop = spike | reversal
    base = valid_r & np.isfinite(w_prev) & (w_prev > 0)
    ok = base & ~drop & (np.abs(r) <= MARKET_MAX_ABS_RET) & ok_w_prev
    out = pd.DataFrame({"ID": df["ID"].to_numpy(), "date": df["date"].to_numpy(),
                        "r": r, "w": w_prev, "ok": ok, "cap_usd": cap_usd,
                        "plausible": plausible})
    out.attrs = {"n_stray_rows": n_stray, "n_constituents": len(ids)}
    return out


def _ff3_book_equity(snap):
    """SF1 ARY book equity per filing: ID, datekey, reportperiod, be.
    SE = equity (assets - liabilities when equity is missing); BE = SE +
    taxliabilities.fillna(0); preferred stock = 0 (BMdec's convention)."""
    have = set(snap.columns("SF1"))
    missing = [c for c in FF3_BE_COLUMNS if c not in have]
    if missing:
        raise KeyError(f"ff3: SF1 has no column(s) {missing}; book equity cannot be built")
    sf1 = snap.table("SF1", FF3_BE_COLUMNS, keep=False)
    sf1 = sf1[sf1["dimension"] == FF3_BE_DIMENSION]
    ids = sf1["ticker"].map(snap.ticker_map("SF1"))
    eq = sf1["equity"].astype(float)
    se = eq.where(eq.notna(), sf1["assets"].astype(float) - sf1["liabilities"].astype(float))
    be = se + sf1["taxliabilities"].astype(float).fillna(0.0)
    out = pd.DataFrame({"ID": ids.to_numpy(), "datekey": pd.to_datetime(sf1["datekey"]).to_numpy(),
                        "reportperiod": pd.to_datetime(sf1["reportperiod"]).to_numpy(),
                        "be": be.to_numpy()})
    return out.dropna(subset=["ID", "datekey", "reportperiod"]).reset_index(drop=True)


def ff3_assignments(nd, be, meta, cfg):
    """The June formations. `nd` is _ff3_name_days' frame, `be` is
    _ff3_book_equity's, `meta` is snap.ticker_meta(). Returns
    (assign, breakpoints): assign has ID, fy (formation year), port (one of
    FF3_PORTS), me_jun, me_dec, be, bm; breakpoints is one row per formed
    year: fy, formed (F_y), size_bp, bm_lo, bm_hi, n_eligible, n_nyse.
    Reads nothing dated after F_y for year y (datekey <= F_y; caps on or
    before F_y)."""
    bp_ex = (cfg["universe"].get("size_breakpoint") or {}).get("exchange", "NYSE")
    tol = pd.Timedelta(days=FF3_ME_TOL_DAYS)
    d = pd.to_datetime(nd["date"])
    mon = d.dt.month
    sub = nd.loc[mon.isin([FF3_FORMATION_MONTH, 12]).to_numpy(), ["ID", "date", "cap_usd", "plausible"]].copy()
    sub["date"] = pd.to_datetime(sub["date"])
    sub["y"] = sub["date"].dt.year
    sub["m"] = sub["date"].dt.month
    last = sub.groupby(["ID", "y", "m"], sort=False).tail(1)
    last_day = d.max()
    exch = meta["exchange"] if "exchange" in meta.columns else pd.Series(dtype=object)
    assigns, bps = [], []
    for yy in sorted(last.loc[last["m"] == FF3_FORMATION_MONTH, "y"].unique()):
        F = ff3_formation_date(yy)
        if F > last_day:
            continue
        dec_end = to_bme([pd.Timestamp(year=int(yy) - 1, month=12, day=31)]).iloc[0]
        jun = last[(last["y"] == yy) & (last["m"] == FF3_FORMATION_MONTH)
                   & (last["date"] <= F) & (last["date"] >= F - tol)].set_index("ID")
        dec = last[(last["y"] == yy - 1) & (last["m"] == 12)
                   & (last["date"] <= dec_end) & (last["date"] >= dec_end - tol)].set_index("ID")
        b = be[(be["reportperiod"].dt.year == yy - 1) & (be["datekey"] <= F)]
        b = (b.sort_values(["ID", "reportperiod", "datekey"], kind="mergesort")
              .groupby("ID", sort=False).tail(1).set_index("ID")["be"])
        me_j = jun["cap_usd"].where(jun["plausible"].astype(bool))
        me_d = dec["cap_usd"].where(dec["plausible"].astype(bool))
        x = pd.DataFrame({"me_jun": me_j}).join(me_d.rename("me_dec"), how="inner").join(b, how="inner")
        x = x[(x["me_jun"] > 0) & (x["me_dec"] > 0) & (x["be"] > 0)]
        if x.empty:
            continue
        x["bm"] = x["be"] / x["me_dec"]
        nyse = x[exch.reindex(x.index).to_numpy() == bp_ex]
        if len(nyse) < FF3_MIN_BREAKPOINT_NAMES:
            raise RuntimeError(
                f"ff3: formation {yy} has {len(nyse)} eligible {bp_ex} names "
                f"(< {FF3_MIN_BREAKPOINT_NAMES}); the harness will not set breakpoints on it.")
        size_bp = float(nyse["me_jun"].quantile(FF3_SIZE_PCTL))
        bm_lo = float(nyse["bm"].quantile(FF3_BM_PCTLS[0]))
        bm_hi = float(nyse["bm"].quantile(FF3_BM_PCTLS[1]))
        size = np.where(x["me_jun"] <= size_bp, "S", "B")
        bmc = np.where(x["bm"] <= bm_lo, "L", np.where(x["bm"] <= bm_hi, "M", "H"))
        x["port"] = np.char.add(size.astype(str), bmc.astype(str))
        x["fy"] = int(yy)
        x.index.name = "ID"
        assigns.append(x.reset_index()[["ID", "fy", "port", "me_jun", "me_dec", "be", "bm"]])
        bps.append({"fy": int(yy), "formed": F, "size_bp": size_bp, "bm_lo": bm_lo,
                    "bm_hi": bm_hi, "n_eligible": int(len(x)), "n_nyse": int(len(nyse))})
    cols = ["ID", "fy", "port", "me_jun", "me_dec", "be", "bm"]
    assign = pd.concat(assigns, ignore_index=True) if assigns else pd.DataFrame(columns=cols)
    return assign, pd.DataFrame(bps, columns=["fy", "formed", "size_bp", "bm_lo", "bm_hi",
                                              "n_eligible", "n_nyse"])


def build_ff3_daily(snap, cfg, log=print):
    """Frame indexed by date (the market calendar): mkt, smb, hml, n_names,
    the six portfolio returns r_SL..r_BH and their name counts n_SL..n_BH.
    See the block comment above for every rule."""
    t0 = time.time()
    nd = _ff3_name_days(snap, cfg)
    nd_attrs = dict(nd.attrs)
    be = _ff3_book_equity(snap)
    assign, bps = ff3_assignments(nd, be, snap.ticker_meta(), cfg)
    if assign.empty:
        raise RuntimeError("ff3: no June formation could be made (no year with December and "
                           "June caps and positive SF1 ARY book equity).")
    ok = nd["ok"].to_numpy()
    x = pd.DataFrame({"ID": nd["ID"].to_numpy()[ok], "date": nd["date"].to_numpy()[ok],
                      "r": nd["r"].to_numpy()[ok], "w": nd["w"].to_numpy()[ok]})
    del nd
    x["wr"] = x["w"] * x["r"]
    g = x.groupby("date", sort=True)
    out = pd.DataFrame({"mkt": g["wr"].sum() / g["w"].sum(),
                        "n_names": g["r"].size().astype("int64")})
    out.index.name = "date"
    thin = out[out["n_names"] < MARKET_MIN_NAMES]
    if len(thin):
        raise RuntimeError(
            f"ff3: {len(thin)} trading day(s) with fewer than {MARKET_MIN_NAMES} names "
            f"(e.g. {thin.index[0].date()}). The calendar or a guard is wrong.")

    yr = x["date"].dt.year
    f_of = {int(y): ff3_formation_date(y) for y in yr.unique()}
    fy = np.where(x["date"] > yr.map(f_of), yr, yr - 1)
    x["fy"] = fy.astype("int64")
    xa = x.merge(assign[["ID", "fy", "port"]], on=["ID", "fy"], how="inner")
    gp = xa.groupby(["date", "port"], sort=True)
    pr = (gp["wr"].sum() / gp["w"].sum()).unstack("port").reindex(index=out.index, columns=list(FF3_PORTS))
    pn = (gp["r"].size().unstack("port").reindex(index=out.index, columns=list(FF3_PORTS))
            .fillna(0).astype("int64"))
    first_formed = pd.Timestamp(bps["formed"].min())
    held = out.index > first_formed
    thin_p = held & (pn.min(axis=1) < FF3_MIN_PORT_NAMES).to_numpy()
    if thin_p.any():
        day = out.index[thin_p][0]
        raise RuntimeError(
            f"ff3: {int(thin_p.sum())} holding day(s) with a portfolio of fewer than "
            f"{FF3_MIN_PORT_NAMES} names (e.g. {day.date()}: {pn.loc[day].to_dict()}). "
            "A formation year is missing or a guard is wrong; the harness will not serve it.")
    pr = pr.where(pd.Series(held, index=out.index), np.nan, axis=0)
    out["smb"] = pr[["SL", "SM", "SH"]].mean(axis=1, skipna=False) - pr[["BL", "BM", "BH"]].mean(axis=1, skipna=False)
    out["hml"] = pr[["SH", "BH"]].mean(axis=1, skipna=False) - pr[["SL", "BL"]].mean(axis=1, skipna=False)
    for p in FF3_PORTS:
        out[f"r_{p}"] = pr[p]
    for p in FF3_PORTS:
        out[f"n_{p}"] = pn[p].where(held, 0).astype("int64")
    out = out[["mkt", "smb", "hml", "n_names"] + [f"r_{p}" for p in FF3_PORTS]
              + [f"n_{p}" for p in FF3_PORTS]]
    out.attrs = {"n_stray_rows": nd_attrs.get("n_stray_rows", 0),
                 "n_formations": int(len(bps)),
                 "first_formed": str(first_formed.date())}
    log(f"    ff3 daily: {len(out):,} days, {int(held.sum()):,} with SMB/HML from "
        f"{len(bps)} June formations ({bps['fy'].min()}-{bps['fy'].max()}), "
        f"median {int(bps['n_eligible'].median()):,} eligible names; dropped "
        f"{nd_attrs.get('n_stray_rows', 0)} stray-date rows; {time.time() - t0:.0f}s")
    return out


def _ff3_builder_sha():
    """Hash of the FF3 builder's source and constants (market rules included,
    since the name-days are the market's), so a code change can never be
    served a parquet built by the previous code."""
    src = "".join(inspect.getsource(f) for f in
                  (market_constituent_ids, market_trading_calendar, _ff3_name_days,
                   _ff3_book_equity, ff3_formation_date, ff3_assignments, build_ff3_daily))
    consts = (MARKET_MAX_ABS_RET, MARKET_SPIKE_UP, MARKET_SPIKE_DOWN, MARKET_REV_AFTER_UP,
              MARKET_REV_AFTER_DOWN, MARKET_PAIR_NET_TOL, MARKET_MAX_CAP_TO_ADV,
              MARKET_ADV_ROWS, MARKET_CAL_WINDOW, MARKET_MIN_DAY_FRAC, MARKET_MIN_NAMES,
              MARKET_VERSION, FF3_FORMATION_MONTH, FF3_SIZE_PCTL, FF3_BM_PCTLS,
              FF3_BE_DIMENSION, FF3_ME_TOL_DAYS, FF3_MIN_BREAKPOINT_NAMES,
              FF3_MIN_PORT_NAMES, FF3_PORTS, FF3_BE_COLUMNS, FF3_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def ff3_cache_key(data_sha, cfg):
    u = cfg["universe"]
    bp_ex = (u.get("size_breakpoint") or {}).get("exchange", "NYSE")
    return hashlib.sha256(
        f"{data_sha}|{sorted(u['exchanges'])}|{sorted(u['categories'])}|"
        f"{u.get('daily_marketcap_scale', 1)}|{bp_ex}|{_ff3_builder_sha()}".encode()
    ).hexdigest()[:12]


def load_or_build_ff3(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = ff3_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"ff3_daily_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    ff3 daily: cache hit {p.name}")
        return pd.read_parquet(p)
    ff3 = build_ff3_daily(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        ff3.to_parquet(p)
        log(f"    ff3 daily: cached as {p.name}")
    return ff3


# =============================================================================
# Monthly market series from the daily name-days: the Pastor-Stambaugh
# aggregate liquidity innovation and the Kelly-Jiang tail-risk factor — built
# once per snapshot, cached on disk
# =============================================================================
#
# Two OSAP predictors load on a MARKET-WIDE MONTHLY SERIES that OSAP reads
# from an upstream file and Sharadar does not publish: BetaLiquidityPS (the
# Pastor-Stambaugh `ps_innov`, from WRDS ff.liq_ps) and BetaTailRisk (Kelly-
# Jiang `tailex`, which OSAP builds itself from all of CRSP daily). The harness
# REBUILDS both from the snapshot, the same class of approximation as the FF3
# rebuild above. Both read the market's own name-days (`_series_name_days`:
# the market builder's constituents, trading calendar, returns and causal
# bad-print guards, repeated rule for rule so build_market_daily and its cache
# key cannot move; a test pins that the value-weighted mean over its `ok` rows
# IS build_market_daily's mkt_ret, exactly). Neither uses the market's WEIGHT
# guard (cap <= 1e5 x ADV) on returns — that guard is about DAILY.marketcap
# errors, not prices — so a name-day's return enters when it passes the RETURN
# guards (`clean`): a valid previous-trading-day return, not a spike (r > +100%
# or r < -80%), not the reversal of one, |r| <= 500%. Both also require
# SEP.volume > 0 on the day (known_traps sep_no_trade_days_are_rows: a no-trade
# day is a row with the price carried forward, a 0 return that CRSP would book
# at the bid/ask midpoint).
#
# ---- Pastor-Stambaugh (2003) aggregate liquidity innovation, `ps_innov` -----
#   * Per stock i and month t, daily OLS over the month's trading days:
#       r^e_{i,d+1} = theta + phi r_{i,d} + gamma sign(r^e_{i,d}) v_{i,d} + e
#     r = the daily closeadj total return; r^e = r - r_m with r_m the market's
#     prior-day-cap-weighted daily return (build_market_daily's mkt_ret,
#     recomputed from the same name-days); v = dollar volume in $ millions,
#     SEP.close x SEP.volume / 1e6 (split-invariant: known_traps
#     sep_volume_split_restated). A regression observation is a PAIR of
#     consecutive market trading days (d, d+1), both in month t, on which the
#     stock traded (volume > 0) with clean returns. PS's "15 observations" is
#     applied to VALID DAILY RETURNS in the month (n_days >= PS_MIN_OBS),
#     not to pairs: a stock trading every day of a D-day month has D returns
#     and D-1 pairs, and 2001-09 (markets shut after 9/11) had 15 trading
#     days, so a >= 15-pairs rule leaves NO eligible stock that month and
#     blanks ps_innov for 2001-09..11 (measured on DATA_SHA 52402f7d1f9c).
#   * NO-TRADE DAYS: a pair needs volume > 0 on BOTH d and d+1. After a
#     zero-volume day d0 (price carried forward) the next traded day d1's
#     return is a TWO-DAY return (close_d1 / last trade - 1); it is a valid
#     return (d0 is the previous market day), so it stays: as x1 of the pair
#     (d1, d2), and in n_days. Pairs (d0-1, d0) and (d0, d1) are dropped.
#   * Eligible (i, t): listed on NYSE or NYSEMKT (AMEX) at the end of t-1
#     (PS's NYSE/AMEX sample; ps_exchange_asof, below); a market constituent (common-stock category —
#     the proxy for CRSP share codes 10/11); a last SEP row of month t-1 dated
#     within PS_PREV_TOL_DAYS of that month's business month-end with
#     closeunadj in [PS_PRICE_LO, PS_PRICE_HI] = [$5, $1000] (PS's price
#     filter, on the unadjusted price) and a positive, PLAUSIBLE (the market's
#     cap <= 1e5 x ADV guard) DAILY.marketcap on that row; >= 15 valid daily
#     returns in t and an identified regression (>= 4 pairs, regressors not
#     constant or collinear).
#   * EXCHANGE AS OF t-1. TICKERS.exchange is today's. Measured on DATA_SHA
#     52402f7d1f9c over 1999-2022, against the exchange in force at the time
#     (reconstructed from ACTIONS exchangeto / exchangefrom pairs) at the end
#     of t-1: of 483,268 today's-NYSE/AMEX eligible name-months, 4.67% were
#     NOT NYSE/AMEX then (21,169 NASDAQ, 1,214 OTC, 168 NYSEARCA) and 4.77%
#     more were missed (NYSE/AMEX then, NASDAQ today); 9.43% differ. The ACTIONS moves cover 15% of tickers and
#     start 1998-01-07, so that is a lower bound. ps_exchange_asof applies
#     PS_EXCHANGE_RULE:
#       "causal" (the default): the destination of the last move dated <= the
#       end of t-1, else TICKERS.exchange. Bytes-causal in ACTIONS, but a name
#       whose only move is AFTER t falls back to today's exchange — wrong at t
#       exactly because the move has not happened — so it corrects only 6,524
#       of the 45,596 misclassified name-months (39,142, 8.10%, remain).
#       "retro": the ORIGIN of the first move dated after t-1 when there is
#       one, else the causal rule. It recovers the exchange actually in force
#       at t — a fact public at t, what CRSP's exchcd records — but reads an
#       ACTIONS row dated after t, the same class of read as TICKERS.exchange
#       itself.
#     The choice matters: gamma_hat is an equal-weighted mean of a per-$M
#     slope, so the ~4.6% of names swapped move the series; corr(ps_innov)
#     1999-2022 today's vs causal 0.974, today's vs retro 0.789, causal vs
#     retro 0.822 (same snapshot).
#   * gamma_hat_t = mean of gamma_{i,t} over eligible i; a month with fewer
#     than PS_MIN_NAMES (100) eligible names is undefined (NaN), and its names
#     do not enter dgamma as t-1 either. m_t = total market
#     value at the end of t-1 of those same stocks (so the sum and the mean
#     run over one set). dgamma_t = (m_t / m_1) x mean over i eligible in BOTH
#     t and t-1 of (gamma_{i,t} - gamma_{i,t-1}). m_1 is the first defined
#     month's m (PS: August 1962): a constant, so it rescales every ps_innov by
#     one positive number, and any per-stock beta on the series by its
#     inverse — a cross-sectional beta RANK is unchanged.
#   * dgamma_t = a + b dgamma_{t-1} + c (m_{t-1}/m_1) gamma_hat_{t-1} + u_t;
#     ps_innov_t = u_hat_t / 100.
#   * CAUSALITY: PS fit that regression on the full sample (look-ahead). Here
#     it is fit on an EXPANDING window of every regression month <= t and
#     ps_innov_t is the residual at t, so no value reads anything after its
#     own month (tested: appending later data leaves every earlier value
#     bit-identical). It is emitted once the window holds PS_MIN_MONTHS (24)
#     months: three coefficients leave 21 degrees of freedom, enough for the
#     AR term not to be noise-fitted, and more would cost months the data
#     cannot spare — DAILY.marketcap starts 1998-12, so m_t (a t-1 cap) is
#     first defined for 1999-01, dgamma for 1999-02, the lagged regressor for
#     1999-03, and the first ps_innov lands about 24 months later (2001-02).
#     Cost of causality, measured on DATA_SHA 52402f7d1f9c over 1999-2022:
#     the AR coefficients drift as the window grows (c = -0.88 at 2001-02,
#     -0.39 at 2022-12); the expanding residual correlates 0.98 with the
#     full-sample one; its AR(1) is 0.13 (Spearman 0.01, 0.02 without 2020)
#     against 0.02 for the full-sample residual.
#   * RESIDUAL CHOICE: the cached ps_innov_t is the per-t expanding residual
#     (each month's residual under the coefficients fit through that month);
#     the path is fixed once written. MonthContext.monthly_ps_innov(...,
#     refit=True) instead re-fits once through the SIGNAL month and returns
#     every s <= t residual under those coefficients (PS's own shape, as of
#     t) — computed per signal date from the cached monthly frame, causal by
#     construction (ps_refit_residuals); its last value equals the expanding
#     one.
#   * SCALE: gamma is per $ million of daily volume and m_1 is 1999's market,
#     not 1962's, so ps_innov has a std of ~2e-5, orders of magnitude below
#     PS's published series.
#     A positive constant: rank-neutral for a beta, immaterial to an OLS.
#   * NOT PS: (a) exchange as of t-1 per PS_EXCHANGE_RULE (above); TICKERS
#     category is CURRENT; a name on OTC / BATS / NYSEARCA today is not a
#     candidate even when ACTIONS shows it on NYSE/AMEX at t-1 (FNMA, FMCC,
#     EVEIQ): <= 0.11% of eligible name-months and <= 0.90% of m_t in any
#     year 1999-2022 (measured above market_constituent_ids); (b)
#     category, not share codes 10/11; (c) no delisting returns, no returns
#     across a trading gap, name-days with r < -80% or r > +100% dropped (the
#     market's guards), no-trade days dropped; (d) the AR fit is expanding,
#     not full-sample; (e) m_1 is 1999-01, not 1962-08; (f) r_m is the
#     harness's raw VW market, not CRSP's.
#
# ---- Kelly-Jiang (2014) tail risk, `tailex` -----------------------------------
#   * For each calendar month m, pool the daily returns of every market
#     constituent name-day passing the return guards with volume > 0 (no
#     price, size or liquidity screen: OSAP pools all of CRSP daily).
#     retp5_m = the TAIL_Q (5th) percentile with "lower" interpolation: the
#     element at floor((n-1) q) of the sorted pool (numpy's and polars'
#     "lower", verified equal). tailex_m = mean of log(r / retp5_m) over r <=
#     retp5_m. A month whose retp5 is not negative is NaN (the ratio would not
#     be positive); returns <= -100% cannot occur (closeadj > 0).
#   * The month holding the snapshot's first trading day is NaN (its first
#     day has no return), and so is a month with fewer than TAIL_MIN_DAYS
#     pooled trading days. tailex needs no DAILY row, so it starts with SEP
#     (1998-01), not with DAILY.marketcap.
#   * A no-trade day is out of the pool; the next traded day's TWO-DAY return
#     (from the carried-forward price) is in it.
#   * Diagnostics on the cached frame: n_spike_dn (name-days with volume > 0
#     dropped by the r < -80% guard) and tailex_unguarded / retp5_unguarded
#     (the same statistic with those name-days put back; every other guard
#     unchanged). The accessor serves the guarded tailex.
#   * NOT Kelly-Jiang / OSAP: (a) the pool is common stock on listed
#     exchanges, not every CRSP security; (b) THE SPIKE GUARD DROPS r < -80%
#     (genuine crashes and bad prints alike), so tailex reads shallower in
#     months holding such days. Measured on DATA_SHA 52402f7d1f9c,
#     1999-2022: 532 traded r < -80% name-days guarded out (225 of 288
#     months hold one, at most 14); |tailex - tailex_unguarded| mean 0.0008,
#     median 0.0006, max 0.0057 in 2003-10 (0.5168 vs 0.5224), against a
#     tailex std of 0.059; the two correlate 0.9999. Small, not first-order;
#     (c) no delisting returns; (d)
#     no-trade days are dropped rather than carried at the bid/ask midpoint.

PS_EXCHANGES = ("NYSE", "NYSEMKT")
PS_PRICE_LO = 5.0
PS_PRICE_HI = 1000.0
PS_MIN_OBS = 15
PS_PREV_TOL_DAYS = 7
PS_MIN_MONTHS = 24
PS_DV_SCALE = 1e6
PS_INNOV_SCALE = 100.0
PS_COLLINEAR_TOL = 1e-12
PS_MIN_NAMES = 100
PS_EXCHANGE_RULE = "retro"         # runner ruling 2026-09-26: the exchange in force at t (public at t), recovered from the origin of the next ACTIONS move; see the block comment
PS_VERSION = "ps-v2"
TAIL_Q = 0.05
TAIL_MIN_DAYS = 15
TAIL_VERSION = "tail-v2"


def _shift_bme(months, k):
    """The business month-end k calendar months after each of `months`."""
    p = pd.PeriodIndex(pd.DatetimeIndex(months), freq="M") + int(k)
    return pd.DatetimeIndex(to_bme(p.to_timestamp(how="start")).to_numpy())


def _series_name_days(snap, cfg):
    """Every constituent row on the market trading calendar with the market
    builder's return and guards, split so a series can take the RETURN guards
    without the weight guard. Frame sorted by ID, date: ID, date, month (its
    business month-end), r, valid_r (a return from the previous market
    trading day), clean (valid_r and no spike / reversal / |r| > 500%),
    spike_dn (valid_r and r < -80%, the down-spike guard alone), ok
    (the market's mask: clean plus a positive, plausible prior-day weight), w
    (prior-day DAILY.marketcap), cap_usd (same-day cap in USD), plausible
    (cap <= 1e5 x trailing 20-row median dollar volume), closeunadj, volume,
    dv (close x volume, USD). The row logic is build_market_daily's, line for
    line; see the block comments above."""
    ids = market_constituent_ids(snap, cfg)
    tmap = snap.ticker_map("SEP")
    tmap = tmap[tmap.isin(ids)]

    sep = snap.table("SEP", ["ticker", "date", "closeadj", "close", "closeunadj", "volume"], keep=False)
    sep = sep.assign(ID=sep["ticker"].map(tmap)).dropna(subset=["ID"])
    sep = sep.assign(dv=sep["close"].astype(float) * sep["volume"].astype(float))
    sep = sep[["ID", "date", "closeadj", "closeunadj", "volume", "dv"]]
    daily = snap.table("DAILY", ["ticker", "date", "marketcap"], keep=False)
    daily = daily.assign(ID=daily["ticker"].map(tmap)).dropna(subset=["ID"])
    daily = daily[["ID", "date", "marketcap"]].drop_duplicates(["ID", "date"], keep="last")

    df = (sep.drop_duplicates(["ID", "date"], keep="last")
             .merge(daily, on=["ID", "date"], how="left")
             .sort_values(["ID", "date"], kind="mergesort")
             .reset_index(drop=True))
    del sep, daily
    cal = market_trading_calendar(df["date"])
    n_stray = int((~df["date"].isin(cal)).sum())
    df = df[df["date"].isin(cal)].reset_index(drop=True)
    prev_mkt_day = pd.Series(cal[:-1], index=cal[1:])

    adv = (df.groupby("ID", sort=False)["dv"]
             .rolling(MARKET_ADV_ROWS, min_periods=1).median()
             .reset_index(level=0, drop=True)
             .reindex(df.index))
    cap_usd = df["marketcap"].to_numpy(dtype=float) * float(cfg["universe"].get("daily_marketcap_scale", 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        plausible = cap_usd <= MARKET_MAX_CAP_TO_ADV * adv.to_numpy(dtype=float)
    same = df["ID"].to_numpy()[1:] == df["ID"].to_numpy()[:-1]
    p_prev = np.r_[np.nan, np.where(same, df["closeadj"].to_numpy()[:-1], np.nan)]
    w_prev = np.r_[np.nan, np.where(same, df["marketcap"].to_numpy(dtype=float)[:-1], np.nan)]
    ok_w_prev = np.r_[False, same & plausible[:-1]]
    d_prev = np.r_[np.datetime64("NaT"), np.where(same, df["date"].to_numpy()[:-1],
                                                  np.datetime64("NaT"))].astype("datetime64[ns]")
    r = df["closeadj"].to_numpy(dtype=float) / p_prev - 1.0
    want_prev = prev_mkt_day.reindex(df["date"]).to_numpy()
    valid_r = (d_prev == want_prev) & np.isfinite(r)
    with np.errstate(invalid="ignore"):
        spike_up = valid_r & (r > MARKET_SPIKE_UP)
        spike_dn = valid_r & (r < MARKET_SPIKE_DOWN)
        spike = spike_up | spike_dn
        prev_up = np.r_[False, spike_up[:-1]] & valid_r
        prev_dn = np.r_[False, spike_dn[:-1]] & valid_r
        r_prev = np.r_[np.nan, r[:-1]]
        net = np.abs((1.0 + r_prev) * (1.0 + r) - 1.0) <= MARKET_PAIR_NET_TOL
        reversal = ((prev_up & (r < MARKET_REV_AFTER_UP)) |
                    (prev_dn & (r > MARKET_REV_AFTER_DOWN))) & net & ~spike
        drop = spike | reversal
        clean = valid_r & ~drop & (np.abs(r) <= MARKET_MAX_ABS_RET)
    base = valid_r & np.isfinite(w_prev) & (w_prev > 0)
    ok = base & ~drop & (np.abs(r) <= MARKET_MAX_ABS_RET) & ok_w_prev
    out = pd.DataFrame({"ID": df["ID"].to_numpy(), "date": df["date"].to_numpy(),
                        "month": to_bme(df["date"]).to_numpy(),
                        "r": r, "valid_r": valid_r, "clean": clean, "spike_dn": spike_dn,
                        "ok": ok, "w": w_prev,
                        "cap_usd": cap_usd, "plausible": plausible,
                        "closeunadj": df["closeunadj"].to_numpy(dtype=float),
                        "volume": df["volume"].to_numpy(dtype=float),
                        "dv": df["dv"].to_numpy(dtype=float)})
    out.attrs = {"n_stray_rows": n_stray, "n_constituents": len(ids),
                 "first_day": str(pd.Timestamp(cal[0]).date()) if len(cal) else None,
                 "n_spike": int(spike.sum()), "n_reversal": int(reversal.sum())}
    return out


def _vw_market_from_name_days(nd):
    """build_market_daily's mkt_ret from `_series_name_days` rows: the
    prior-day-cap-weighted mean over `ok` name-days, per date."""
    ok = nd["ok"].to_numpy()
    w = nd["w"].to_numpy()[ok]
    x = pd.DataFrame({"date": nd["date"].to_numpy()[ok], "wr": w * nd["r"].to_numpy()[ok], "w": w})
    g = x.groupby("date", sort=True)
    return (g["wr"].sum() / g["w"].sum()).rename("mkt_ret")


def ps_gamma_from_pairs(pairs):
    """Per (ID, month) OLS of y on a constant, x1 and x2 — PS's
    r^e_{d+1} = theta + phi r_d + gamma sign(r^e_d) v_d. `pairs` has
    columns ID, month, y, x1, x2 (one row per observation). Returns a frame
    indexed by (ID, month): gamma, phi, n_obs. Solved in closed form on the
    within-group centred cross-products (the intercept is partialled out), so
    ~1M regressions are one groupby; gamma is NaN when either regressor has
    no variance or the two are collinear (1 - corr^2 <= PS_COLLINEAR_TOL) or
    n_obs < 4 (three coefficients and a residual)."""
    keys = ["ID", "month"]
    p = pairs[keys + ["y", "x1", "x2"]]
    g = p.groupby(keys, sort=True)
    mu = g[["y", "x1", "x2"]].transform("mean")
    y = p["y"].to_numpy(float) - mu["y"].to_numpy(float)
    a = p["x1"].to_numpy(float) - mu["x1"].to_numpy(float)
    b = p["x2"].to_numpy(float) - mu["x2"].to_numpy(float)
    c = pd.DataFrame({"ID": p["ID"].to_numpy(), "month": p["month"].to_numpy(),
                      "aa": a * a, "ab": a * b, "bb": b * b, "ay": a * y, "by": b * y})
    s = c.groupby(keys, sort=True).sum()
    n = g.size().reindex(s.index)
    aa, ab, bb = s["aa"].to_numpy(), s["ab"].to_numpy(), s["bb"].to_numpy()
    ay, by = s["ay"].to_numpy(), s["by"].to_numpy()
    det = aa * bb - ab * ab
    with np.errstate(divide="ignore", invalid="ignore"):
        good = (aa > 0) & (bb > 0) & (det > PS_COLLINEAR_TOL * aa * bb) & (n.to_numpy() >= 4)
        gamma = np.where(good, (aa * by - ab * ay) / det, np.nan)
        phi = np.where(good, (bb * ay - ab * by) / det, np.nan)
    return pd.DataFrame({"gamma": gamma, "phi": phi, "n_obs": n.to_numpy().astype("int64")},
                        index=s.index)


def _exchange_moves(snap):
    """ACTIONS exchange moves paired per (ID, date): ID, date, ex_to (the
    `exchangeto` row's contraname, the destination), ex_from (the
    `exchangefrom` row's, the origin). Empty when the snapshot holds none."""
    cols = ["ID", "date", "ex_to", "ex_from"]
    if not snap.has("ACTIONS") or "contraname" not in snap.columns("ACTIONS"):
        return pd.DataFrame(columns=cols)
    a = snap.table("ACTIONS", ["date", "action", "ticker", "contraname"])
    a = a[a["action"].isin(["exchangeto", "exchangefrom"])]
    if a.empty:
        return pd.DataFrame(columns=cols)
    a = a.assign(ID=a["ticker"].map(snap.ticker_map("ACTIONS")),
                 date=pd.to_datetime(a["date"])).dropna(subset=["ID", "date"])
    to = a[a["action"] == "exchangeto"].groupby(["ID", "date"])["contraname"].last().rename("ex_to")
    fr = a[a["action"] == "exchangefrom"].groupby(["ID", "date"])["contraname"].last().rename("ex_from")
    mv = pd.concat([to, fr], axis=1).reset_index()
    return mv.sort_values(["date", "ID"], kind="mergesort").reset_index(drop=True)[cols]


def ps_exchange_asof(ids, dates, moves, current, rule=None):
    """The exchange of each (ID, date), an array aligned with the inputs.
    `moves` is _exchange_moves' frame, `current` TICKERS.exchange by ID.
    rule "causal": the destination of the last move dated <= date, else
    `current` (reads no ACTIONS row after the date). rule "retro": the origin
    of the first move dated after the date when there is one, else the
    causal answer (the exchange in force at the date, from a later-dated
    row). Default PS_EXCHANGE_RULE; see the block comment."""
    rule = PS_EXCHANGE_RULE if rule is None else rule
    if rule not in ("causal", "retro"):
        raise ValueError(f"exchange rule must be 'causal' or 'retro', not {rule!r}")
    left = (pd.DataFrame({"ID": np.asarray(ids, dtype=object),
                          "t": pd.to_datetime(np.asarray(dates))})
              .reset_index().sort_values("t", kind="mergesort"))
    res = pd.Series(current.reindex(left["ID"]).to_numpy(), index=left["index"].to_numpy(), dtype=object)
    if len(moves) and len(left):
        mv = moves.rename(columns={"date": "t"}).astype({"ID": object})
        mv["t"] = pd.to_datetime(mv["t"])
        to = mv.dropna(subset=["ex_to"]).sort_values("t", kind="mergesort")[["ID", "t", "ex_to"]]
        got = pd.merge_asof(left, to, on="t", by="ID", direction="backward")
        asof = pd.Series(got["ex_to"].to_numpy(), index=got["index"].to_numpy(), dtype=object)
        asof = asof.reindex(res.index)
        if rule == "retro":
            fr = mv.dropna(subset=["ex_from"]).sort_values("t", kind="mergesort")[["ID", "t", "ex_from"]]
            nx = pd.merge_asof(left, fr, on="t", by="ID", direction="forward", allow_exact_matches=False)
            nxt = pd.Series(nx["ex_from"].to_numpy(), index=nx["index"].to_numpy(), dtype=object)
            nxt = nxt.reindex(res.index)
            asof = nxt.where(nxt.notna(), asof)
        res = asof.where(asof.notna(), res)
    return res.sort_index().to_numpy()


def ps_stock_months(snap, cfg, nd=None):
    """Per (ID, month) for every constituent that could be on NYSE/AMEX at
    some point (today's TICKERS.exchange, or an ACTIONS move to or from
    one): gamma, phi, n_obs (regression pairs), n_days (valid daily returns
    in the month: clean, traded, with a market return — the count PS_MIN_OBS
    applies to), exchange (as of the end of t-1, ps_exchange_asof), px_prev
    (closeunadj on the last row of month t-1), cap_prev (its DAILY cap in
    USD, NaN when implausible), prev_date, and `eligible` (every PS rule in
    the block comment). Returns (stock_months, info) where info holds the
    daily market series used for r^e and pair counts."""
    nd = _series_name_days(snap, cfg) if nd is None else nd
    rm = _vw_market_from_name_days(nd)
    meta = snap.ticker_meta()
    ex = meta["exchange"] if "exchange" in meta.columns else pd.Series(dtype=object)
    moves = _exchange_moves(snap)
    ps_ex = list(PS_EXCHANGES)
    cand = set(ex.index[ex.isin(ps_ex).to_numpy()])
    cand |= set(moves.loc[(moves["ex_to"].isin(ps_ex) | moves["ex_from"].isin(ps_ex)).to_numpy(), "ID"])
    sub = nd[nd["ID"].isin(cand)].reset_index(drop=True)

    r = sub["r"].to_numpy()
    re = r - rm.reindex(sub["date"]).to_numpy()
    vol_ok = sub["volume"].to_numpy() > 0
    good = sub["clean"].to_numpy() & vol_ok & np.isfinite(re)
    ids = sub["ID"].to_numpy()
    mon = sub["month"].to_numpy()
    pair = ((ids[1:] == ids[:-1]) & good[:-1] & good[1:] & sub["valid_r"].to_numpy()[1:]
            & (mon[1:] == mon[:-1]))
    j = np.flatnonzero(pair)
    pairs = pd.DataFrame({"ID": ids[j + 1], "month": mon[j + 1], "y": re[j + 1], "x1": r[j],
                          "x2": np.sign(re[j]) * sub["dv"].to_numpy()[j] / PS_DV_SCALE})
    gam = ps_gamma_from_pairs(pairs).reset_index()
    n_days = (pd.Series(1, index=pd.MultiIndex.from_arrays([ids[good], mon[good]], names=["ID", "month"]))
                .groupby(level=["ID", "month"]).size().rename("n_days").reset_index())
    gam = gam.merge(n_days, on=["ID", "month"], how="left")
    gam["exchange"] = ps_exchange_asof(gam["ID"], _shift_bme(gam["month"], -1), moves, ex)

    last = sub.groupby(["ID", "month"], sort=False).tail(1)
    prev = pd.DataFrame({"ID": last["ID"].to_numpy(),
                         "month": _shift_bme(last["month"], 1),
                         "prev_me": last["month"].to_numpy(),
                         "prev_date": last["date"].to_numpy(),
                         "px_prev": last["closeunadj"].to_numpy(),
                         "cap_prev": np.where(last["plausible"].to_numpy(dtype=bool),
                                              last["cap_usd"].to_numpy(), np.nan)})
    sm = gam.merge(prev, on=["ID", "month"], how="left")
    fresh = (pd.to_datetime(sm["prev_date"])
             >= pd.to_datetime(sm["prev_me"]) - pd.Timedelta(days=PS_PREV_TOL_DAYS))
    sm["eligible"] = (fresh.to_numpy()
                      & sm["exchange"].isin(ps_ex).to_numpy()
                      & (sm["px_prev"] >= PS_PRICE_LO).to_numpy()
                      & (sm["px_prev"] <= PS_PRICE_HI).to_numpy()
                      & (sm["cap_prev"] > 0).to_numpy()
                      & (sm["n_days"] >= PS_MIN_OBS).to_numpy()
                      & np.isfinite(sm["gamma"].to_numpy()))
    info = {"rm": rm, "n_pairs": int(len(pairs)), "n_ps_name_days": int(len(sub)),
            "zero_volume_share": float((~vol_ok & sub["clean"].to_numpy()).sum()
                                       / max(int(sub["clean"].sum()), 1))}
    return sm.drop(columns=["prev_me"]), info


def ps_aggregate(elig, min_names=None):
    """`elig`: one row per eligible (ID, month) with gamma and cap_prev.
    Frame indexed by every business month-end from the first to the last
    (contiguous, so a shift is one month): gamma_hat, n_eligible, m_usd,
    m_scale (m_t / m_1, m_1 = the first DEFINED month's m), dgamma_raw (the
    mean change over names eligible in t and t-1), n_both, dgamma
    (= m_scale x dgamma_raw). A month with fewer than `min_names` (default
    PS_MIN_NAMES) eligible names is undefined: gamma_hat, m_usd, dgamma NaN,
    and its names do not enter dgamma of the next month either
    (n_eligible still reports its count)."""
    cols = ["gamma_hat", "n_eligible", "m_usd", "m_scale", "dgamma_raw", "n_both", "dgamma"]
    if elig.empty:
        return pd.DataFrame(columns=cols, index=pd.DatetimeIndex([], name="me"))
    min_names = PS_MIN_NAMES if min_names is None else int(min_names)
    cnt = elig.groupby("month", sort=True).size()
    months = pd.DatetimeIndex(cnt.index)
    per = pd.period_range(months.min(), months.max(), freq="M")
    full = pd.DatetimeIndex(to_bme(per.to_timestamp(how="start")).to_numpy(), name="me")
    out = pd.DataFrame(np.nan, index=full, columns=cols)
    out["n_eligible"] = cnt.reindex(full).fillna(0).astype("int64").to_numpy()
    out["n_both"] = 0
    keep = cnt.index[cnt.to_numpy() >= min_names]
    e = elig[elig["month"].isin(keep)]
    out.attrs = {"m1_month": None, "min_names": min_names}
    if e.empty:
        return out[cols]
    g = e.groupby("month", sort=True)
    out["gamma_hat"] = g["gamma"].mean().reindex(full).to_numpy()
    out["m_usd"] = g["cap_prev"].sum().reindex(full).to_numpy()
    first = pd.Timestamp(min(keep))
    out["m_scale"] = out["m_usd"] / float(out.loc[first, "m_usd"])
    prev = pd.DataFrame({"ID": e["ID"].to_numpy(), "month": _shift_bme(e["month"], 1),
                         "gamma_prev": e["gamma"].to_numpy()})
    both = e[["ID", "month", "gamma"]].merge(prev, on=["ID", "month"], how="inner")
    bg = (both["gamma"] - both["gamma_prev"]).groupby(both["month"].to_numpy())
    out["dgamma_raw"] = bg.mean().reindex(full).to_numpy()
    out["n_both"] = bg.size().reindex(full).fillna(0).astype("int64").to_numpy()
    out["dgamma"] = out["m_scale"] * out["dgamma_raw"]
    out.attrs["m1_month"] = str(first.date())
    return out[cols]


def _ps_design(agg):
    """(y, X, rows) of the AR regression on ps_aggregate's contiguous frame:
    y_t = dgamma_t, X_t = [1, dgamma_{t-1}, m_scale_{t-1} gamma_hat_{t-1}],
    rows = positions where all are finite."""
    idx = pd.DatetimeIndex(agg.index)
    if len(idx) > 1 and not (pd.DatetimeIndex(_shift_bme(idx[:-1], 1)) == idx[1:]).all():
        raise RuntimeError("ps_innovations: the monthly frame is not contiguous; a shift "
                           "would not be one month.")
    y = agg["dgamma"].to_numpy(float)
    x1 = np.r_[np.nan, y[:-1]]
    lvl = (agg["m_scale"] * agg["gamma_hat"]).to_numpy(float)
    x2 = np.r_[np.nan, lvl[:-1]]
    rows = np.flatnonzero(np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2))
    return y, np.column_stack([np.ones(len(y)), x1, x2]), rows


def ps_innovations(agg, min_months=None):
    """The expanding-window innovation. For each t with >= `min_months`
    (default PS_MIN_MONTHS) complete regression months <= t, OLS on those
    months and ps_innov_t = (y_t - X_t b_t) / PS_INNOV_SCALE (_ps_design).
    Reads nothing after t. Frame on agg's index: ps_a, ps_b, ps_c (b_t),
    n_fit, ps_innov."""
    min_months = PS_MIN_MONTHS if min_months is None else int(min_months)
    y, X_all, rows = _ps_design(agg)
    out = pd.DataFrame(np.nan, index=pd.DatetimeIndex(agg.index),
                       columns=["ps_a", "ps_b", "ps_c", "n_fit", "ps_innov"])
    for k, pos in enumerate(rows):
        n_fit = k + 1
        if n_fit < min_months:
            continue
        use = rows[:n_fit]
        coef, *_ = np.linalg.lstsq(X_all[use], y[use], rcond=None)
        u = y[pos] - X_all[pos] @ coef
        out.iloc[pos] = [coef[0], coef[1], coef[2], n_fit, u / PS_INNOV_SCALE]
    return out


def ps_refit_residuals(agg, min_months=None):
    """PS's full-sample residuals AS OF the last month of `agg`: one OLS on
    every complete regression month in the frame, the residual of each / 100.
    Series on agg's index, NaN where a month is not a regression month and
    everywhere when fewer than `min_months` (default PS_MIN_MONTHS) exist.
    Causal when the caller passes only months <= the signal (the
    monthly_ps_innov(refit=True) accessor does); its last value then equals
    ps_innovations' value for that month."""
    min_months = PS_MIN_MONTHS if min_months is None else int(min_months)
    y, X_all, rows = _ps_design(agg)
    out = pd.Series(np.nan, index=pd.DatetimeIndex(agg.index), name="ps_innov")
    if len(rows) < min_months:
        return out
    coef, *_ = np.linalg.lstsq(X_all[rows], y[rows], rcond=None)
    out.iloc[rows] = (y[rows] - X_all[rows] @ coef) / PS_INNOV_SCALE
    return out


def build_ps_innov_monthly(snap, cfg, log=print):
    """Frame indexed by business month-end (`me`): gamma_hat, n_eligible,
    m_usd, m_scale, dgamma_raw, n_both, dgamma, ps_a, ps_b, ps_c, n_fit,
    ps_innov (NaN until the expanding fit holds PS_MIN_MONTHS months). See
    the block comment above for every rule and deviation."""
    t0 = time.time()
    nd = _series_name_days(snap, cfg)
    nd_attrs = dict(nd.attrs)
    sm, info = ps_stock_months(snap, cfg, nd=nd)
    del nd
    elig = sm[sm["eligible"]]
    agg = ps_aggregate(elig)
    inn = ps_innovations(agg)
    out = agg.join(inn)
    first = out["ps_innov"].first_valid_index()
    out.attrs = {"m1_month": agg.attrs.get("m1_month"), "n_pairs": info["n_pairs"],
                 "zero_volume_share": info["zero_volume_share"],
                 "n_stray_rows": nd_attrs.get("n_stray_rows", 0),
                 "first_ps_innov": str(first.date()) if first is not None else None}
    log(f"    ps_innov monthly: {len(out)} months from {agg.attrs.get('m1_month')}, "
        f"{info['n_pairs']:,} daily pairs, median {int(out['n_eligible'].median()) if len(out) else 0:,} "
        f"eligible NYSE/AMEX names, first ps_innov {out.attrs['first_ps_innov']}; "
        f"{info['zero_volume_share'] * 100:.2f}% of clean name-days had no volume; "
        f"{time.time() - t0:.0f}s")
    return out


def _ps_builder_sha():
    """Hash of the PS builder's source and constants (market rules included,
    since the name-days are the market's)."""
    src = "".join(inspect.getsource(f) for f in
                  (market_constituent_ids, market_trading_calendar, to_bme, _shift_bme,
                   _series_name_days, _vw_market_from_name_days, ps_gamma_from_pairs,
                   _exchange_moves, ps_exchange_asof, ps_stock_months, ps_aggregate,
                   _ps_design, ps_innovations, build_ps_innov_monthly))
    consts = (MARKET_MAX_ABS_RET, MARKET_SPIKE_UP, MARKET_SPIKE_DOWN, MARKET_REV_AFTER_UP,
              MARKET_REV_AFTER_DOWN, MARKET_PAIR_NET_TOL, MARKET_MAX_CAP_TO_ADV,
              MARKET_ADV_ROWS, MARKET_CAL_WINDOW, MARKET_MIN_DAY_FRAC, MARKET_MIN_NAMES,
              MARKET_VERSION, PS_EXCHANGES, PS_PRICE_LO, PS_PRICE_HI, PS_MIN_OBS,
              PS_PREV_TOL_DAYS, PS_MIN_MONTHS, PS_DV_SCALE, PS_INNOV_SCALE, PS_COLLINEAR_TOL,
              PS_MIN_NAMES, PS_EXCHANGE_RULE, PS_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def ps_cache_key(data_sha, cfg):
    u = cfg["universe"]
    return hashlib.sha256(
        f"{data_sha}|{sorted(u['exchanges'])}|{sorted(u['categories'])}|"
        f"{u.get('daily_marketcap_scale', 1)}|ps|{_ps_builder_sha()}".encode()
    ).hexdigest()[:12]


def load_or_build_ps(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = ps_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"ps_innov_monthly_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    ps_innov monthly: cache hit {p.name}")
        return pd.read_parquet(p)
    ps = build_ps_innov_monthly(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        ps.to_parquet(p)
        log(f"    ps_innov monthly: cached as {p.name}")
    return ps


def tailex_from_pool(month, r, q=TAIL_Q):
    """Kelly-Jiang's monthly tail statistic from a pooled sample. `month`
    labels each return. Frame indexed by month: retp5 (the q-quantile,
    "lower": the element at floor((n-1) q) of the sorted month), tailex (mean
    of log(r / retp5) over r <= retp5; NaN when retp5 >= 0), n_pooled,
    n_tail."""
    df = pd.DataFrame({"month": np.asarray(month), "r": np.asarray(r, dtype=float)})
    df = df[np.isfinite(df["r"].to_numpy())]
    if df.empty:
        return pd.DataFrame(columns=["retp5", "tailex", "n_pooled", "n_tail"])
    df = df.sort_values(["month", "r"], kind="mergesort").reset_index(drop=True)
    n = df.groupby("month", sort=True).size()
    start = (n.cumsum() - n).to_numpy()
    k = np.floor((n.to_numpy() - 1) * q).astype(np.int64)
    p5 = pd.Series(df["r"].to_numpy()[start + k], index=n.index)
    thr = p5.reindex(df["month"]).to_numpy()
    tail = df["r"].to_numpy() <= thr
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = df["r"].to_numpy()[tail] / thr[tail]
        lg = np.where(ratio > 0, np.log(ratio), np.nan)
    t = pd.Series(lg).groupby(df["month"].to_numpy()[tail])
    out = pd.DataFrame({"retp5": p5, "tailex": t.mean().reindex(n.index),
                        "n_pooled": n.astype("int64"),
                        "n_tail": t.size().reindex(n.index).fillna(0).astype("int64")})
    out.loc[~(out["retp5"] < 0), "tailex"] = np.nan
    return out


def build_tailex_monthly(snap, cfg, log=print):
    """Frame indexed by business month-end (`me`): retp5, tailex, n_pooled
    (pooled name-days), n_tail, n_days (trading days in the pool), and the
    guard diagnostics n_spike_dn (traded name-days dropped by the r < -80%
    guard), retp5_unguarded and tailex_unguarded (the statistic with those
    name-days put back, every other guard unchanged). See the block comment
    above for every rule and deviation."""
    t0 = time.time()
    nd = _series_name_days(snap, cfg)
    traded = nd["volume"].to_numpy() > 0
    pool = nd["clean"].to_numpy() & traded
    dn = nd["spike_dn"].to_numpy() & traded
    n_clean = int(nd["clean"].sum())
    months = nd["month"].to_numpy()
    r = nd["r"].to_numpy()
    mon = months[pool]
    tx = tailex_from_pool(mon, r[pool])
    un = tailex_from_pool(months[pool | dn], r[pool | dn])
    n_days = pd.Series(nd["date"].to_numpy()[pool]).groupby(mon).nunique()
    n_dn = pd.Series(1, index=months[dn]).groupby(level=0).size()
    first_day = pd.Timestamp(nd["date"].min())
    del nd
    tx["n_days"] = n_days.reindex(tx.index).fillna(0).astype("int64")
    tx["n_spike_dn"] = n_dn.reindex(tx.index).fillna(0).astype("int64")
    tx["retp5_unguarded"] = un["retp5"].reindex(tx.index)
    tx["tailex_unguarded"] = un["tailex"].reindex(tx.index)
    tx.index = pd.DatetimeIndex(tx.index, name="me")
    blank = (tx.index == to_bme([first_day]).iloc[0]) | (tx["n_days"] < TAIL_MIN_DAYS).to_numpy()
    tx.loc[blank, ["retp5", "tailex", "retp5_unguarded", "tailex_unguarded"]] = np.nan
    tx.attrs = {"n_pool": int(pool.sum()), "zero_volume_share": 1.0 - pool.sum() / max(n_clean, 1),
                "n_blank": int(blank.sum()), "n_spike_dn": int(dn.sum())}
    log(f"    tailex monthly: {int(tx['tailex'].notna().sum())} months, {int(pool.sum()):,} pooled "
        f"name-days ({tx.attrs['zero_volume_share'] * 100:.2f}% of clean name-days dropped for "
        f"no volume), {int(dn.sum()):,} traded r < -80% name-days guarded out; "
        f"{time.time() - t0:.0f}s")
    return tx[["retp5", "tailex", "n_pooled", "n_tail", "n_days", "n_spike_dn",
               "retp5_unguarded", "tailex_unguarded"]]


def _tailex_builder_sha():
    src = "".join(inspect.getsource(f) for f in
                  (market_constituent_ids, market_trading_calendar, to_bme, _series_name_days,
                   tailex_from_pool, build_tailex_monthly))
    consts = (MARKET_MAX_ABS_RET, MARKET_SPIKE_UP, MARKET_SPIKE_DOWN, MARKET_REV_AFTER_UP,
              MARKET_REV_AFTER_DOWN, MARKET_PAIR_NET_TOL, MARKET_MAX_CAP_TO_ADV,
              MARKET_ADV_ROWS, MARKET_CAL_WINDOW, MARKET_MIN_DAY_FRAC, MARKET_MIN_NAMES,
              MARKET_VERSION, TAIL_Q, TAIL_MIN_DAYS, TAIL_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def tailex_cache_key(data_sha, cfg):
    u = cfg["universe"]
    return hashlib.sha256(
        f"{data_sha}|{sorted(u['exchanges'])}|{sorted(u['categories'])}|"
        f"{u.get('daily_marketcap_scale', 1)}|tailex|{_tailex_builder_sha()}".encode()
    ).hexdigest()[:12]


def load_or_build_tailex(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = tailex_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"tailex_monthly_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    tailex monthly: cache hit {p.name}")
        return pd.read_parquet(p)
    tx = build_tailex_monthly(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        tx.to_parquet(p)
        log(f"    tailex monthly: cached as {p.name}")
    return tx


# =============================================================================
# Han-Zhou-Zhu (2016) trend-factor coefficients, `trend` — built once, cached
# =============================================================================
#
# OSAP's TrendFactor (Predictors/TrendFactor.py at b4e911e6) is a linear
# prediction: sum_L EBeta_L(t) x A_L(i, t). A_L is the normalised moving
# average of the daily price, EBeta the trailing mean of monthly cross-
# sectional slopes of next-month return on the A_L. The slopes are a MARKET
# series (one vector per month, fit on all of CRSP), so they are built here,
# once; the factor computes A_L(i, t) for its universe names through
# MonthContext.trend_ma_signals (the same pure function the builder uses) and
# dots it with MonthContext.monthly_trend_coefs.
#
#   * MA SIGNALS (trend_ma_signals). P = SEP.close (split-adjusted, NO
#     dividend adjustment: OSAP's |prc| / cfacpr). Per name, over ALL its SEP
#     rows in date order (no-trade rows included — SEP carries them with the
#     price forward, close to CRSP's bid/ask-midpoint rows; no calendar or
#     volume filter; duplicate (ID, date) rows keep the last),
#     for L in TREND_LAGS = 3, 5, ... 1000 rows:
#     A_L = mean(P over the last L rows, fewer when the name has fewer —
#     OSAP asrol min_samples=1, PARTIAL WINDOWS ALLOWED) / P, evaluated at
#     the name's LAST row DATED <= the business month-end in each business
#     month (OSAP keeps _n == _N per month; a stray weekend row after the
#     BME, e.g. a Saturday calendar month-end, is never the month's row, so
#     it can neither be the signal row nor the return/fit(m) row — it stays
#     in LATER months' window history, where it is a past print). A null close is skipped in the mean and in its count (Stata's
#     asrol); a null close on the month's last row makes every A_L null.
#     `close` is restated to today's split basis (known_trap
#     close_is_split_adjusted); A_L is a ratio of the same series, so a
#     common rescaling cancels (tested). Window sums come from per-name
#     cumulative sums evaluated only at month-end rows, O(rows) per lag.
#   * ELIGIBLE fit(m) — OSAP's regression sample, imposed on the SIGNAL
#     stage: a market constituent (market_constituent_ids: common-stock
#     category — the proxy for share codes 10/11 — and today's TICKERS
#     exchange in universe.exchanges) whose exchange IN FORCE at BME(m)
#     (ps_exchange_asof, rule PS_EXCHANGE_RULE, the Pastor-Stambaugh
#     precedent) is in universe.exchanges (OSAP exchcd 1/2/3), with a row in
#     month m whose closeunadj >= TREND_PRICE_MIN ($5, OSAP |prc| >= 5, on
#     the unadjusted price) and whose DAILY.marketcap (USD, the market's
#     cap <= 1e5 x ADV plausibility guard) is >= the TREND_SIZE_PCTL (10th)
#     percentile of that month's caps of names on TREND_SIZE_EXCHANGE (NYSE)
#     at BME(m) (OSAP qu10 over exchcd == 1; pandas linear quantile, the
#     universe breakpoint's; no price screen in the breakpoint set, as in
#     OSAP). A month with fewer than TREND_MIN_NYSE such NYSE names has no
#     cut and no fit names. No freshness rule: OSAP's month-end price is
#     the last trade of the month, wherever it falls.
#   * REGRESSION for month m (the row's index, `me`): y = the month-m total
#     return closeadj(last row in m) / closeadj(last row in m-1) - 1 of
#     every name fit at m-1 (fit_month) with a row in m; X = [1, A_L at
#     m-1]. TREND_REQUIRE_FIT_NEXT: OSAP builds fRet as a lead of the
#     ALREADY-FILTERED frame, so the name must ALSO be fit(m) — a name that
#     falls below $5 or the size cut in m, changes to a non-listed exchange,
#     or has no row in m, is out of that month's regression (survivor
#     conditioning inside the fit, OSAP's; the count dropped is the
#     `n_drop_next` diagnostic). OLS by crosssection.ols_coef: Stata-style
#     deterministic collinear omission (the EARLIER of identical columns
#     keeps the weight, the later gets 0), all-NaN below TREND_MIN_OBS rows.
#   * INDEXING — BY THE MONTH AT WHOSE END A ROW IS KNOWN. beta_m (row m)
#     regresses the month-m return on A at m-1, so it is known at the end of
#     m. OSAP's b(s) regresses ret(s+1) on A(s) and EBeta(t) = mean of
#     b(t-12 .. t-1) (.shift(1).rolling(12, min 1)); with beta_m = b(m-1)
#     that is ebar_t = mean(beta_{t-11} .. beta_t), a plain trailing
#     TREND_BETA_WINDOW (12) month mean with no shift, >= TREND_MIN_BETAS (1,
#     OSAP's min_samples) non-null betas. Every column of row t reads nothing
#     after BME(t), so one "<= signal" cut serves every column (tested: a
#     build on data cut at BME(t) equals the full build through t, bit for
#     bit). The index is contiguous (a missing regression month is a NaN
#     row, and the 12-month window is calendar, not row, based — OSAP's
#     row-based window differs only if a month were missing; none is).
#   * COVERAGE / LEFT-CENSORING. DAILY.marketcap starts 1998-12-01, so the
#     first fit month is 1998-12 and the first beta and ebar are 1999-01
#     (ebar_1999-01 rests on ONE beta). SEP starts 1997-12-31, so at BME(s)
#     the snapshot holds n_cal(s) market trading days (the constituents'
#     trading calendar, market_trading_calendar); every A_L with L >=
#     n_cal(s) is the name's full-history mean, IDENTICAL across those L for
#     every name — exactly collinear, the later ones omitted (coefficient 0,
#     `n_dropped`) — and for n_cal(s) a little above L the long columns
#     differ only for the oldest names (near-collinear, large offsetting
#     coefficients). `ma_full` (row m: n_cal(fit_month) >= max(TREND_LAGS),
#     so no A_L at m-1 is truncated by the data start) and `ebar_full` (all
#     TREND_BETA_WINDOW betas in the window present and ma_full) flag it; the
#     factor chooses whether to score censored months (spec sec. 8 options
#     (a)/(b)). This is a DATA-START censoring, not a young-stock rule:
#     partial windows for genuinely young names are OSAP's own.
#   * NOT OSAP: (a) exchange in force per PS_EXCHANGE_RULE, category CURRENT
#     (not share codes); a name listed then but on OTC / delisted-exchange
#     today is not a constituent, as for the market series (measured above
#     market_constituent_ids: <= 0.073% of fit name-months a year, NYSE cut
#     <= 0.36%, 1999-2022); (b) size is
#     DAILY.marketcap per permaticker (company-level for multi-class firms),
#     not CRSP mve_c per permno; (c) NO DELISTING RETURNS: a name with no
#     row in m has no fRet (and is not fit(m)); a name that dies inside m
#     earns its return to its last trade (and is out if it fails fit(m));
#     (d) no return guard: fRet is the raw closeadj ratio (the fit sample's
#     $5 / NYSE-p10 screens at both ends remove most bad prints;
#     `n_abs_ret_gt5` and `max_abs_ret` are diagnostics); (e) SEP no-trade
#     rows stand in for CRSP's bid/ask-midpoint rows; (f) data-start
#     censoring above; (g) the breakpoint is a pandas linear quantile, not
#     Stata's _pctile (at most one order statistic apart).

TREND_LAGS = (3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000)
TREND_PRICE_MIN = 5.0
TREND_SIZE_PCTL = 10.0
TREND_SIZE_EXCHANGE = "NYSE"
TREND_MIN_NYSE = 20
TREND_REQUIRE_FIT_NEXT = True
TREND_MIN_OBS = 30
TREND_BETA_WINDOW = 12
TREND_MIN_BETAS = 1
TREND_DAYS_BACK = 1800             # accessor: calendar days of SEP read for 1000 rows (~1,240 trading days)
TREND_TOL_DAYS = 7                 # accessor: the name's last row within this many days of the signal
TREND_VERSION = "trend-v1"


def trend_ma_cols(lags=None):
    return [f"A_{int(L)}" for L in (TREND_LAGS if lags is None else lags)]


def trend_ma_signals(rows, lags=None, carry=()):
    """Normalised moving averages at each name's last row per business month.
    `rows`: a long frame with ID, date, close (any order; the name's full
    row history or a trailing window of it) plus any `carry` columns. Rows
    are sorted by (ID, date) stably and duplicate (ID, date) rows keep the
    last. Returns one row per (ID, month): ID, month (business month-end),
    date (that row's), close, n_rows (non-null closes through that row),
    the `carry` columns from that row, and A_<L> = mean(close over the last
    L rows, fewer when fewer exist; null closes skipped) / close. The
    month's row is the last one DATED <= the business month-end: a row after
    the BME inside the calendar month (a weekend print) is never evaluated
    and never enters that month's window (it follows the evaluated row); it
    does sit in later months' windows. A month whose only rows fall after
    its BME has no row. Pure: reads no row after the one it evaluates."""
    lags = tuple(int(L) for L in (TREND_LAGS if lags is None else lags))
    carry = [c for c in carry if c not in ("ID", "date", "close")]
    cols = ["ID", "month", "date", "close", "n_rows"] + list(carry) + trend_ma_cols(lags)
    if len(rows) == 0:
        return pd.DataFrame(columns=cols)
    df = rows[["ID", "date", "close"] + list(carry)].copy()
    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")
    df = (df.sort_values(["ID", "date"], kind="mergesort")
            .drop_duplicates(["ID", "date"], keep="last").reset_index(drop=True))
    n = len(df)
    ids = df["ID"].to_numpy()
    month = to_bme(df["date"]).to_numpy()
    new = np.r_[True, ids[1:] != ids[:-1]]
    start = np.maximum.accumulate(np.where(new, np.arange(n), 0))
    x = df["close"].to_numpy(dtype=float)
    ok = np.isfinite(x)
    grp = np.cumsum(new) - 1
    cs = pd.Series(np.where(ok, x, 0.0)).groupby(grp).cumsum().to_numpy()
    cc = pd.Series(ok.astype(np.int64)).groupby(grp).cumsum().to_numpy()
    inb = np.flatnonzero(df["date"].to_numpy() <= month)   # rows dated on/before their BME
    bi, bm = ids[inb], month[inb]
    i = inb[np.r_[(bi[1:] != bi[:-1]) | (bm[1:] != bm[:-1]), True]] if len(inb) else inb
    out = pd.DataFrame({"ID": ids[i], "month": month[i], "date": df["date"].to_numpy()[i],
                        "close": x[i], "n_rows": cc[i]})
    for c in carry:
        out[c] = df[c].to_numpy()[i]
    xi = x[i]
    for L in lags:
        j = i - L                                   # the row just before the window
        inside = j >= start[i]
        s = cs[i] - np.where(inside, cs[np.maximum(j, 0)], 0.0)
        c = cc[i] - np.where(inside, cc[np.maximum(j, 0)], 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[f"A_{L}"] = np.where((c > 0) & np.isfinite(xi) & (xi != 0), s / c / xi, np.nan)
    return out[cols]


def trend_stock_months(snap, cfg, nd=None):
    """Per (ID, month) for every market constituent: the month's last SEP
    row with date, close, closeadj, closeunadj, n_rows, A_<L>
    (trend_ma_signals over the name's full SEP history), cap_usd (DAILY on
    that date, NaN when implausible or missing), exchange (in force at the
    business month-end, ps_exchange_asof), cut_usd (the month's NYSE
    TREND_SIZE_PCTL cap) and `fit` (OSAP's regression-sample rule; block
    comment). Returns (stock_months, info) with info = {"n_cal": Series of
    market trading days <= each month-end, ...}."""
    nd = _series_name_days(snap, cfg) if nd is None else nd
    m_end = nd.groupby(["ID", "month"], sort=False).tail(1)
    capf = pd.DataFrame({"ID": m_end["ID"].to_numpy(), "date": m_end["date"].to_numpy(),
                         "cap_usd": np.where(m_end["plausible"].to_numpy(dtype=bool),
                                             m_end["cap_usd"].to_numpy(dtype=float), np.nan)})
    cal = pd.DatetimeIndex(np.sort(nd["date"].unique()))
    del nd, m_end

    ids = market_constituent_ids(snap, cfg)
    tmap = snap.ticker_map("SEP")
    tmap = tmap[tmap.isin(ids)]
    sep = snap.table("SEP", ["ticker", "date", "close", "closeadj", "closeunadj"], keep=False)
    sep = sep.assign(ID=sep["ticker"].map(tmap)).dropna(subset=["ID"])
    sep = sep[["ID", "date", "close", "closeadj", "closeunadj"]]
    sm = trend_ma_signals(sep, carry=("closeadj", "closeunadj"))
    del sep
    sm = sm.merge(capf, on=["ID", "date"], how="left")
    del capf

    meta = snap.ticker_meta()
    cur = meta["exchange"] if "exchange" in meta.columns else pd.Series(dtype=object)
    sm["exchange"] = ps_exchange_asof(sm["ID"], sm["month"], _exchange_moves(snap), cur,
                                      rule=PS_EXCHANGE_RULE)
    listed = sm["exchange"].isin(list(cfg["universe"]["exchanges"])).to_numpy()
    cap = sm["cap_usd"].to_numpy(dtype=float)
    ref = sm[(sm["exchange"] == TREND_SIZE_EXCHANGE).to_numpy() & (cap > 0)]
    g = ref.groupby("month")["cap_usd"]
    cut = g.quantile(TREND_SIZE_PCTL / 100.0).where(g.size() >= TREND_MIN_NYSE)
    sm["cut_usd"] = cut.reindex(sm["month"]).to_numpy()
    with np.errstate(invalid="ignore"):
        sm["fit"] = (listed & (sm["closeunadj"].to_numpy(dtype=float) >= TREND_PRICE_MIN)
                     & (cap > 0) & (cap >= sm["cut_usd"].to_numpy(dtype=float)))
    months = pd.DatetimeIndex(np.sort(sm["month"].unique()))
    n_cal = pd.Series(cal.searchsorted(months, side="right"), index=months, name="n_cal")
    return sm, {"n_cal": n_cal, "first_day": str(cal[0].date()) if len(cal) else None}


def trend_regressions(sm, n_cal=None, lags=None):
    """The monthly cross-sectional regressions on `sm` (trend_stock_months'
    frame: ID, month, closeadj, fit, A_<L>). Frame indexed by every business
    month-end `me` from the month after the first fit month to the last
    month (contiguous): fit_month (me - 1), n_fit (fit names at fit_month),
    n_obs (regression rows), n_drop_next (rows lost to
    TREND_REQUIRE_FIT_NEXT), n_dropped (collinear columns omitted),
    n_abs_ret_gt5, max_abs_ret, ma_full (n_cal(fit_month) >= max lag; False
    when n_cal is not given), b_const, b_A_<L>. Row me reads only months
    <= me."""
    lags = tuple(TREND_LAGS if lags is None else lags)
    acols = trend_ma_cols(lags)
    bcols = ["b_const"] + [f"b_{c}" for c in acols]
    diag = ["fit_month", "n_fit", "n_obs", "n_drop_next", "n_dropped", "n_abs_ret_gt5",
            "max_abs_ret", "ma_full"]
    fit = sm[sm["fit"].to_numpy(dtype=bool)]
    if fit.empty:
        return pd.DataFrame(columns=diag + bcols, index=pd.DatetimeIndex([], name="me"))
    first = pd.Timestamp(fit["month"].min())
    last = pd.Timestamp(sm["month"].max())
    per = pd.period_range(first, last, freq="M")[1:]
    idx = pd.DatetimeIndex(to_bme(per.to_timestamp(how="start")).to_numpy(), name="me")
    out = pd.DataFrame(np.nan, index=idx, columns=diag + bcols)
    out["fit_month"] = pd.DatetimeIndex(_shift_bme(idx, -1)) if len(idx) else pd.NaT
    if len(idx) == 0:
        return out
    prev = pd.DataFrame({"ID": fit["ID"].to_numpy(), "me": _shift_bme(fit["month"], 1),
                         "p0": fit["closeadj"].to_numpy(dtype=float)})
    for c in acols:
        prev[c] = fit[c].to_numpy(dtype=float)
    cur = pd.DataFrame({"ID": sm["ID"].to_numpy(), "me": pd.DatetimeIndex(sm["month"]),
                        "p1": sm["closeadj"].to_numpy(dtype=float),
                        "fit_now": sm["fit"].to_numpy(dtype=bool)})
    reg = prev.merge(cur, on=["ID", "me"], how="inner")
    with np.errstate(divide="ignore", invalid="ignore"):
        reg["y"] = reg["p1"] / reg["p0"] - 1.0
    reg = reg[np.isfinite(reg["y"].to_numpy())]
    n_fit = fit.groupby("month").size()
    out["n_fit"] = n_fit.reindex(pd.DatetimeIndex(out["fit_month"])).fillna(0).to_numpy()
    lost = (~reg["fit_now"]).groupby(reg["me"]).sum() if TREND_REQUIRE_FIT_NEXT else pd.Series(dtype=float)
    out["n_drop_next"] = lost.reindex(idx).fillna(0).to_numpy()
    if TREND_REQUIRE_FIT_NEXT:
        reg = reg[reg["fit_now"].to_numpy()]
    for me, g in reg.groupby("me", sort=True):
        if me not in out.index:
            continue
        b = ols_coef(g["y"], g[acols], add_intercept=True, min_obs=TREND_MIN_OBS)
        ay = np.abs(g["y"].to_numpy())
        out.loc[me, bcols] = b.to_numpy()
        out.loc[me, ["n_obs", "n_dropped", "n_abs_ret_gt5", "max_abs_ret"]] = [
            b.attrs["n_obs"], len(b.attrs["dropped"]), int((ay > MARKET_MAX_ABS_RET).sum()),
            float(ay.max()) if len(ay) else np.nan]
    for c in ("n_fit", "n_obs", "n_drop_next", "n_dropped", "n_abs_ret_gt5"):
        out[c] = out[c].fillna(0).astype("int64")
    if n_cal is not None:
        nc = pd.Series(n_cal).reindex(pd.DatetimeIndex(out["fit_month"])).to_numpy(dtype=float)
        out["ma_full"] = nc >= max(lags)
    else:
        out["ma_full"] = False
    out["ma_full"] = out["ma_full"].astype(bool)
    return out


def trend_ebar(betas, lags=None):
    """ebar_t = the mean of the non-null betas in the TREND_BETA_WINDOW
    business months ending at t (rows t-11 .. t), >= TREND_MIN_BETAS of them
    (OSAP: shift(1).rolling(12, min_samples=1) on the fit-month index, which
    is this window on the known-at index). Frame on betas' index: n_betas,
    ebar_full (a full window of betas every one of which is ma_full),
    ebar_const, ebar_A_<L>. Refuses a non-contiguous index (a row shift
    must be one month)."""
    lags = tuple(TREND_LAGS if lags is None else lags)
    idx = pd.DatetimeIndex(betas.index)
    if len(idx) > 1 and not (pd.DatetimeIndex(_shift_bme(idx[:-1], 1)) == idx[1:]).all():
        raise RuntimeError("trend_ebar: the monthly frame is not contiguous; a 12-row "
                           "window would not be 12 months.")
    names = ["const"] + trend_ma_cols(lags)
    w, k = int(TREND_BETA_WINDOW), int(TREND_MIN_BETAS)
    b = betas[[f"b_{c}" for c in names]].astype(float)
    ok = b["b_const"].notna()
    n = ok.astype(float).rolling(w, min_periods=1).sum()
    full_b = (ok & betas["ma_full"].astype(bool)).astype(float).rolling(w, min_periods=1).sum()
    out = pd.DataFrame(index=idx)
    out["n_betas"] = n.astype("int64").to_numpy()
    out["ebar_full"] = (full_b == w).to_numpy()
    e = b.rolling(w, min_periods=k).mean()
    for c in names:
        out[f"ebar_{c}"] = e[f"b_{c}"].to_numpy()
    return out


def build_trend_monthly(snap, cfg, log=print):
    """Frame indexed by business month-end `me` (the month at whose end the
    row is known): trend_regressions' columns (beta_me: the month-me return
    on A at me-1) joined with trend_ebar's (ebar_me: the mean of beta over
    me-11 .. me) and n_cal_fit (trading days in the snapshot through
    fit_month), cut_usd (the NYSE size cut at fit_month). See the block
    comment above for every rule and deviation."""
    t0 = time.time()
    sm, info = trend_stock_months(snap, cfg)
    betas = trend_regressions(sm, n_cal=info["n_cal"])
    cut = sm.groupby("month")["cut_usd"].first()
    n_stock_months = len(sm)
    del sm
    out = betas.join(trend_ebar(betas))
    fm = pd.DatetimeIndex(out["fit_month"])
    out["n_cal_fit"] = info["n_cal"].reindex(fm).fillna(0).astype("int64").to_numpy()
    out["cut_usd"] = cut.reindex(fm).to_numpy(dtype=float)
    first = out["ebar_const"].first_valid_index()
    first_full = out.index[out["ebar_full"].to_numpy()].min() if out["ebar_full"].any() else None
    out.attrs = {"first_day": info["first_day"], "n_stock_months": int(n_stock_months),
                 "first_ebar": str(first.date()) if first is not None else None,
                 "first_ebar_full": str(first_full.date()) if first_full is not None else None}
    log(f"    trend monthly: {len(out)} months, {int(out['b_const'].notna().sum())} regressions, "
        f"median {int(out['n_obs'].median()) if len(out) else 0:,} names, first ebar "
        f"{out.attrs['first_ebar']}, first uncensored ebar {out.attrs['first_ebar_full']}; "
        f"{time.time() - t0:.0f}s")
    return out


def _trend_builder_sha():
    """Hash of the trend builder's source and constants: the market rules
    (the name-days' caps and calendar), the exchange-in-force rule and the
    OLS (crosssection.ols_coef) included."""
    src = "".join(inspect.getsource(f) for f in
                  (market_constituent_ids, market_trading_calendar, to_bme, _shift_bme,
                   _series_name_days, _exchange_moves, ps_exchange_asof, trend_ma_cols,
                   trend_ma_signals, trend_stock_months, trend_regressions, trend_ebar,
                   build_trend_monthly, ols_coef))
    consts = (MARKET_MAX_ABS_RET, MARKET_SPIKE_UP, MARKET_SPIKE_DOWN, MARKET_REV_AFTER_UP,
              MARKET_REV_AFTER_DOWN, MARKET_PAIR_NET_TOL, MARKET_MAX_CAP_TO_ADV,
              MARKET_ADV_ROWS, MARKET_CAL_WINDOW, MARKET_MIN_DAY_FRAC, MARKET_MIN_NAMES,
              MARKET_VERSION, PS_EXCHANGE_RULE, TREND_LAGS, TREND_PRICE_MIN, TREND_SIZE_PCTL,
              TREND_SIZE_EXCHANGE, TREND_MIN_NYSE, TREND_REQUIRE_FIT_NEXT, TREND_MIN_OBS,
              TREND_BETA_WINDOW, TREND_MIN_BETAS, TREND_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def trend_cache_key(data_sha, cfg):
    u = cfg["universe"]
    return hashlib.sha256(
        f"{data_sha}|{sorted(u['exchanges'])}|{sorted(u['categories'])}|"
        f"{u.get('daily_marketcap_scale', 1)}|trend|{_trend_builder_sha()}".encode()
    ).hexdigest()[:12]


def load_or_build_trend(snap, cfg, runtime, data_sha, root=ROOT, log=print):
    key = trend_cache_key(data_sha, cfg)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"trend_monthly_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    trend monthly: cache hit {p.name}")
        return pd.read_parquet(p)
    tr = build_trend_monthly(snap, cfg, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        tr.to_parquet(p)
        log(f"    trend monthly: cached as {p.name}")
    return tr


# =============================================================================
# Corwin-Schultz spread series — the construction layer's cost input (D7 item 2)
# =============================================================================
# The Phase E cost model charges half a measured bid-ask spread per name per
# month. It is built here, from SEP daily high / low / close / volume, so the
# cost model never depends on which factors the composite accepted
# (docs/DECISIONS.md D7 item 2; CONSTRUCTION.md §6). Read ONLY by
# `run_test.py --construction-layer`; no factor, universe or Stage 1-3 number
# reads it.
#
# The construction is OSAP's BidAskSpread (the Corwin and Schultz 2011
# program) exactly as translated in factors/candidates/BidAskSpread.py,
# reproduced line for line below (the harness never imports a factor file):
#   1. screen: low == high, low <= 0, high <= 0, close <= 0 or volume == 0 ->
#      that day's low/high are missing;
#   2. a screened day takes the retained range of the ID's last good day
#      (close inside it: copied; below / above: shifted to the close);
#   3. high/low > 8 is dropped;
#   4. overnight adjustment against the previous row's close;
#   5. the two-day estimator: beta = ln(H/L)^2 summed over the two days,
#      gamma = ln(two-day max H / two-day min L)^2,
#      alpha = (sqrt(2 beta) - sqrt(beta)) / (3 - 2 sqrt 2) - sqrt(gamma / (3 - 2 sqrt 2)),
#      S = 2 (e^alpha - 1) / (1 + e^alpha); a NEGATIVE daily estimate is set to 0;
#   6. the month's value is the plain mean of the daily estimates dated in the
#      calendar month of the signal date, NaN when fewer than CS_MIN_DAYS.
# Each month runs the recursion on the SEP rows with
# signal - CS_DAYS_BACK days < date <= signal, the window the factor reads, so
# the retained range and the overnight lag are seeded where the factor seeds
# them and the value equals the factor's raw output name by name. The
# factor's history gate is a scoring gate of the search, not part of the
# value, and is not applied. A month in which SEP holds only part of its
# trading days (the snapshot's first month) is not estimated.
# The stored value is the FULL proportional (round-trip) spread, OSAP's unit;
# the layer charges half of it. Point in time: month m's value uses daily
# rows dated on or before m's signal date only.

CS_DAYS_BACK = 125
CS_MIN_DAYS = 12
CS_VERSION = 1
_CS_C = 3.0 - 2.0 * np.sqrt(2.0)


def cs_daily_spread(df):
    """Daily Corwin-Schultz spread (negatives set to 0) for rows sorted by
    (ID, date); `df` has ID, high, low, close, volume. NaN where the program
    yields none. Line for line the BidAskSpread factor's `_daily_spread`."""
    g = df["ID"].to_numpy()
    hi = df["high"].to_numpy(dtype=float)
    lo = df["low"].to_numpy(dtype=float)
    px = df["close"].to_numpy(dtype=float)
    vol = df["volume"].to_numpy(dtype=float)

    with np.errstate(invalid="ignore", divide="ignore"):
        # 1. screen
        bad = (lo == hi) | (lo <= 0) | (hi <= 0) | (px <= 0) | (vol == 0)
        lo1 = np.where(bad, np.nan, lo)
        hi1 = np.where(bad, np.nan, hi)

        # 2. retained range = last good range at or before the row, per ID
        good = (lo1 > 0) & (lo1 < hi1)
        ret = pd.DataFrame({"g": g, "lo": np.where(good, lo1, np.nan),
                            "hi": np.where(good, hi1, np.nan)})
        rlo = ret.groupby("g")["lo"].ffill().to_numpy()
        rhi = ret.groupby("g")["hi"].ffill().to_numpy()
        within = (rlo <= px) & (px <= rhi)
        below = px < rlo
        above = px > rhi
        lo2 = np.where(good, lo1, np.where(within, rlo, np.where(below, px, np.where(above, rlo + (px - rhi), np.nan))))
        hi2 = np.where(good, hi1, np.where(within, rhi, np.where(below, rhi - (rlo - px), np.where(above, px, np.nan))))

        # 3. high/low > 8 is dropped
        drop = (lo2 != 0) & (hi2 / lo2 > 8)
        lo2 = np.where(drop, np.nan, lo2)
        hi2 = np.where(drop, np.nan, hi2)

        # 4. overnight adjustment; lags are the previous row of the same ID
        pr = pd.DataFrame({"g": g, "lo": lo2, "hi": hi2, "px": px})
        sh = pr.groupby("g")[["lo", "hi", "px"]].shift(1)
        llo, lhi, lpx = sh["lo"].to_numpy(), sh["hi"].to_numpy(), sh["px"].to_numpy()
        c1 = (lpx < lo2) & (lpx > 0)
        c2 = (lpx > hi2) & (lpx > 0)
        thi = np.where(c2, lpx, np.where(c1, hi2 - (lo2 - lpx), hi2))
        tlo = np.where(c2, lo2 + (lpx - hi2), np.where(c1, lpx, lo2))

        # 5. beta, gamma, alpha, spread
        ok = (tlo > 0) & (llo > 0) & (thi > 0) & (lhi > 0)
        beta = np.where(ok, np.log(thi / tlo) ** 2 + np.log(lhi / llo) ** 2, np.nan)
        hi_2 = np.maximum(thi, lhi)
        lo_2 = np.minimum(tlo, llo)
        gamma = np.where(lo_2 > 0, np.log(hi_2 / lo_2) ** 2, np.nan)
        alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / _CS_C - np.sqrt(gamma / _CS_C)
        spread = 2.0 * np.tanh(alpha / 2.0)          # = 2(e^a - 1)/(1 + e^a)
        spread0 = np.where(np.isfinite(spread), np.maximum(spread, 0.0), np.nan)
    return spread0


def table_partial_months(snap, table="SEP"):
    """Calendar months (pd.Period "M") in which `table` holds only part of the
    month's trading days because the snapshot starts inside it. The same rule
    as MonthContext.partial_months, for a builder that has no MonthContext."""
    d = pd.to_datetime(snap.table(table, ["date"], keep=False)["date"])
    first = d.min()
    if pd.notna(first):
        month_first_bday = pd.offsets.BMonthBegin().rollback(first.normalize())
        if first.normalize() > month_first_bday:
            return frozenset({first.to_period("M")})
    return frozenset()


def cs_spread_monthly(daily, signal_dates, partial=frozenset()):
    """The monthly Corwin-Schultz spread for every ID in `daily` (ID, date,
    high, low, close, volume, in the snapshot's row order) at each signal
    date. Frame: me (the signal date), ID, cs_spread (NaN when fewer than
    CS_MIN_DAYS daily estimates), cs_n_days (the count of daily estimates in
    the signal month). Names with no daily estimate that month are absent."""
    dates = daily["date"].to_numpy(dtype="datetime64[ns]")
    order = np.argsort(dates, kind="stable")
    sd = dates[order]
    out = []
    for s in signal_dates:
        s = pd.Timestamp(s)
        month = s.to_period("M")
        if month in partial:
            continue
        lo = np.searchsorted(sd, np.datetime64(s - pd.Timedelta(days=CS_DAYS_BACK)), side="right")
        hi = np.searchsorted(sd, np.datetime64(s), side="right")
        if hi <= lo:
            continue
        d = daily.iloc[np.sort(order[lo:hi])]                 # the window, in snapshot row order
        d = d.sort_values(["ID", "date"], kind="mergesort").reset_index(drop=True)
        d["s0"] = cs_daily_spread(d)
        cur = d[(d["date"].dt.to_period("M") == month) & d["s0"].notna()]
        if cur.empty:
            continue
        grp = cur.groupby("ID")["s0"]
        n = grp.count()
        mean = grp.mean()
        out.append(pd.DataFrame({"me": s, "ID": n.index, "cs_spread": mean.where(n >= CS_MIN_DAYS).to_numpy(),
                                 "cs_n_days": n.to_numpy().astype("int64")}))
    if not out:
        return pd.DataFrame({"me": pd.Series(dtype="datetime64[ns]"), "ID": pd.Series(dtype=object),
                             "cs_spread": pd.Series(dtype=float), "cs_n_days": pd.Series(dtype="int64")})
    cs = pd.concat(out, ignore_index=True)
    cs["me"] = pd.to_datetime(cs["me"]).astype("datetime64[ns]")
    return cs


def build_cs_spread_monthly(snap, log=print):
    """cs_spread_monthly over every SEP row whose ticker maps to an ID, at the
    business month-end of every calendar month SEP covers. IDs are str
    (permaticker), as everywhere in the harness."""
    t0 = time.time()
    tmap = snap.ticker_map("SEP")
    sep = snap.table("SEP", ["ticker", "date", "high", "low", "close", "volume"], keep=False)
    ids = sep["ticker"].map(tmap)
    keep = ids.notna().to_numpy()
    codes, labels = pd.factorize(ids[keep], sort=False)
    daily = pd.DataFrame({"ID": codes.astype(np.int64),
                          "date": pd.to_datetime(sep["date"]).to_numpy()[keep],
                          "high": sep["high"].to_numpy(dtype=float)[keep],
                          "low": sep["low"].to_numpy(dtype=float)[keep],
                          "close": sep["close"].to_numpy(dtype=float)[keep],
                          "volume": sep["volume"].to_numpy(dtype=float)[keep]})
    del sep, ids
    signal_dates = sorted(pd.unique(to_bme(pd.Series(pd.unique(daily["date"])))))
    cs = cs_spread_monthly(daily, signal_dates, table_partial_months(snap, "SEP"))
    cs["ID"] = np.asarray(labels, dtype=object)[cs["ID"].to_numpy(dtype=np.int64)].astype(str)
    ok = cs["cs_spread"].notna()
    log(f"    cs spread monthly: {cs['me'].nunique()} months, {int(ok.sum()):,} name-months with >= "
        f"{CS_MIN_DAYS} daily estimates ({100 * float(ok.mean()) if len(cs) else 0:.1f}% of "
        f"{len(cs):,}); {time.time() - t0:.0f}s")
    return cs[["me", "ID", "cs_spread", "cs_n_days"]]


def _cs_builder_sha():
    """The builder's source and constants, plus the snapshot readers it goes
    through (Snapshot.table, Snapshot.ticker_map): DATA_SHA covers the bytes,
    this covers how they are read and mapped to IDs."""
    src = "".join(inspect.getsource(f) for f in
                  (to_bme, cs_daily_spread, table_partial_months, cs_spread_monthly, build_cs_spread_monthly,
                   Snapshot.table, Snapshot.ticker_map))
    consts = (CS_DAYS_BACK, CS_MIN_DAYS, CS_VERSION)
    return hashlib.sha256((src + repr(consts)).encode()).hexdigest()[:12]


def cs_spread_cache_key(data_sha):
    """Keyed on DATA_SHA and the builder's source: the series reads SEP and
    TICKERS only, through no universe parameter."""
    return hashlib.sha256(f"{data_sha}|cs_spread|{_cs_builder_sha()}".encode()).hexdigest()[:12]


def load_or_build_cs_spread(snap, runtime, data_sha, root=ROOT, log=print):
    key = cs_spread_cache_key(data_sha)
    cache_dir = Path(root) / runtime["cache"]["dir"]
    p = cache_dir / f"cs_spread_monthly_{key}.parquet"
    if runtime["cache"].get("enabled", True) and p.exists():
        log(f"    cs spread monthly: cache hit {p.name}")
        return pd.read_parquet(p)
    cs = build_cs_spread_monthly(snap, log=log)
    if runtime["cache"].get("enabled", True):
        cache_dir.mkdir(parents=True, exist_ok=True)
        cs.to_parquet(p)
        log(f"    cs spread monthly: cached as {p.name}")
    return cs


# =============================================================================
# Delistings
# =============================================================================

def classify_delistings(panel, snap, cfg):
    """Per ID: last trade date, whether the name is delisted (stopped trading
    before the snapshot's end), and the kind — 'merger' (non-performance) when
    a configured non-performance ACTION sits within the reason window of the
    last trade and no performance action does; otherwise 'performance', which
    is also the default for a delisting with no recorded reason (Shumway's
    treatment of unknown codes). The lists are config, the reasons are
    Sharadar's own.
    """
    r = cfg["returns"]["delisting"]
    stale = pd.Timedelta(days=int(cfg["universe"]["max_price_staleness_days"]))
    last = panel.groupby("ID")["date"].max().rename("last_trade")
    snap_end = panel["date"].max()
    delisted = last < (snap_end - stale)

    acts = snap.table("ACTIONS", REQUIRED_COLUMNS["ACTIONS"]).copy()
    acts["date"] = pd.to_datetime(acts["date"])
    acts["ID"] = acts["ticker"].map(snap.ticker_map("ACTIONS"))
    acts = acts.dropna(subset=["ID"]).merge(last, left_on="ID", right_index=True, how="inner")
    win = pd.Timedelta(days=int(r["reason_window_days"]))
    near = acts[(acts["date"] - acts["last_trade"]).abs() <= win]
    non_perf = set(near[near["action"].isin(list(r["non_performance_actions"]))]["ID"])
    perf = set(near[near["action"].isin(list(r.get("performance_actions", [])))]["ID"])
    merger_ids = non_perf - perf

    out = pd.DataFrame({"last_trade": last, "delisted": delisted})
    out["kind"] = np.where(~out["delisted"], "none",
                           np.where(out.index.isin(list(merger_ids)), "merger", "performance"))
    return out


# =============================================================================
# Universe and returns for one month
# =============================================================================

def _assign_tier_pctl(pctl, tier_pctl):
    if pd.isna(pctl):
        return "EXCLUDED"
    for tier in ["MEGA", "MID", "SMALL"]:
        if pctl >= tier_pctl[tier]:
            return tier
    return "EXCLUDED"


class PanelIndex:
    """Fast lookups over the monthly panel: rows by month-end, and the closeadj
    matrix for lookbacks. Built once per run."""

    def __init__(self, panel, snap, cfg):
        self.cfg = cfg
        self.panel = panel
        self.by_me = {me: g for me, g in panel.groupby("me", sort=False)}
        self.months = sorted(self.by_me)
        self.close_wide = panel.pivot(index="ID", columns="me", values="closeadj")
        self.date_wide = panel.pivot(index="ID", columns="me", values="date")
        self.meta = snap.ticker_meta()
        self.delist = classify_delistings(panel, snap, cfg)
        self._snap = snap
        self._market = None
        self._market_loader = None
        self._ff3 = None
        self._ff3_loader = None
        self._ps = None
        self._ps_loader = None
        self._tailex = None
        self._tailex_loader = None
        self._trend = None
        self._trend_loader = None
        self._first = None
        self._first_loader = None
        # Universe membership by month-end, for the hysteresis chain
        # (build_universe). Filled forward from the first panel month.
        self.membership = {}

    def prev_month_end(self, me):
        me = pd.Timestamp(me)
        earlier = [m for m in self.months if m < me]
        return earlier[-1] if earlier else None

    def set_market_loader(self, loader):
        """A zero-argument callable returning the market-daily frame (the
        runner passes load_or_build_market with its DATA_SHA, so the build is
        cached on disk). Called at most once, on the first market_daily read;
        a run whose factors never ask for the market never builds it."""
        self._market_loader = loader
        self._market = None

    def market(self):
        if self._market is None:
            self._market = (self._market_loader() if self._market_loader is not None
                            else build_market_daily(self._snap, self.cfg, log=lambda *a, **k: None))
        return self._market

    def set_ff3_loader(self, loader):
        """A zero-argument callable returning the FF3-daily frame (the runner
        passes load_or_build_ff3 with its DATA_SHA). Called at most once, on
        the first ff3_daily read; a run whose factors never ask for FF3 never
        builds it."""
        self._ff3_loader = loader
        self._ff3 = None

    def ff3(self):
        if self._ff3 is None:
            self._ff3 = (self._ff3_loader() if self._ff3_loader is not None
                         else build_ff3_daily(self._snap, self.cfg, log=lambda *a, **k: None))
        return self._ff3

    def set_ps_loader(self, loader):
        """A zero-argument callable returning the monthly Pastor-Stambaugh
        frame (the runner passes load_or_build_ps with its DATA_SHA). Called
        at most once, on the first monthly_ps_innov read."""
        self._ps_loader = loader
        self._ps = None

    def ps(self):
        if self._ps is None:
            self._ps = (self._ps_loader() if self._ps_loader is not None
                        else build_ps_innov_monthly(self._snap, self.cfg, log=lambda *a, **k: None))
        return self._ps

    def set_tailex_loader(self, loader):
        """A zero-argument callable returning the monthly Kelly-Jiang tail
        frame (the runner passes load_or_build_tailex with its DATA_SHA).
        Called at most once, on the first monthly_tailex read."""
        self._tailex_loader = loader
        self._tailex = None

    def tailex(self):
        if self._tailex is None:
            self._tailex = (self._tailex_loader() if self._tailex_loader is not None
                            else build_tailex_monthly(self._snap, self.cfg, log=lambda *a, **k: None))
        return self._tailex

    def set_trend_loader(self, loader):
        """A zero-argument callable returning the monthly trend-coefficient
        frame (the runner passes load_or_build_trend with its DATA_SHA).
        Called at most once, on the first monthly_trend_coefs read."""
        self._trend_loader = loader
        self._trend = None

    def trend(self):
        if self._trend is None:
            self._trend = (self._trend_loader() if self._trend_loader is not None
                           else build_trend_monthly(self._snap, self.cfg, log=lambda *a, **k: None))
        return self._trend

    def set_first_trade_loader(self, loader):
        """A zero-argument callable returning the first-trade-of-month frame
        (the runner passes load_or_build_first_trade with its DATA_SHA, and
        only under `--return-start skip1`). Called at most once."""
        self._first_loader = loader
        self._first = None

    def first_trade_rows(self, me):
        """Frame indexed by ID (first_date, first_closeadj) for the names'
        first trade in the calendar month of business month-end `me`; None
        when no name traded that month."""
        if self._first is None:
            fr = (self._first_loader() if self._first_loader is not None
                  else build_first_trade_monthly(self._snap, log=lambda *a, **k: None))
            fr = fr.assign(me=pd.to_datetime(fr["me"]), first_date=pd.to_datetime(fr["first_date"]))
            self._first = {m: g.set_index("ID")[["first_date", "first_closeadj"]]
                           for m, g in fr.groupby("me", sort=False)}
        return self._first.get(pd.Timestamp(me))

    def month_rows(self, me):
        return self.by_me.get(pd.Timestamp(me))

    def next_month_end(self, me):
        me = pd.Timestamp(me)
        later = [m for m in self.months if m > me]
        return later[0] if later else None


def relative_size_cut(df, bp):
    """Market-cap floor for one month: the `pctl` percentile of `exchange`
    names' caps in `df` (the Fama-French NYSE breakpoint). Falls back to the
    whole cross-section when the exchange has fewer than `min_names` names
    that month, and returns None when no breakpoint is configured."""
    if not bp:
        return None
    ref = df
    if "exchange" in df.columns and bp.get("exchange"):
        on_ex = df[df["exchange"] == bp["exchange"]]
        if len(on_ex) >= int(bp.get("min_names", 1)):
            ref = on_ex
    if ref.empty:
        return None
    return float(ref["mkt_cap_usd"].quantile(float(bp["pctl"]) / 100.0))


def _hysteresis_on(cfg):
    u = cfg["universe"]
    return bool(u.get("membership_hysteresis", False))


def membership(pidx, me, cfg):
    """The set of IDs in the universe at month-end `me`, under the hysteresis
    chain: month m's membership depends on month m-1's, and the chain starts
    COLD (no prior members) at the first month the panel holds. So a month's
    universe is a function of (config, data, month) only, never of which
    month a run happened to ask for first: `--holdout-only` and
    `--include-holdout` agree on 2023-01, and a Stage 1 batch and a Stage 2
    ladder see the same names. Memoised on the panel index for the run."""
    me = pd.Timestamp(me)
    if me in pidx.membership:
        return pidx.membership[me]
    # Walk back to the first month that is already known (or the panel start),
    # then fill forward. Iterative, so a 30-year chain does not recurse.
    chain = []
    cur = me
    while cur is not None and cur not in pidx.membership:
        chain.append(cur)
        cur = pidx.prev_month_end(cur)
    prev_ids = pidx.membership.get(cur) if cur is not None else None
    for m in reversed(chain):
        ids = frozenset(screen_month(pidx, m, cfg, prev_ids).index)
        pidx.membership[m] = ids
        prev_ids = ids
    return pidx.membership[me]


def build_universe(pidx, signal_asof, cfg):
    """The investable universe as of one signal date, from that date's rows.

    Returns a frame indexed by ID with region, liq_tier, sector, industry,
    exchange, px_usd, mkt_cap_usd, adv_usd, adv_pctl_region and the month's
    entry/exit cuts, one region. With `universe.membership_hysteresis` the
    relative cuts carry a band: a name ENTERS at the configured percentile
    and a current member LEAVES only below the (lower) exit percentile, so
    names sitting on the boundary do not flicker in and out month to month.
    Absolute screens (exchange, category, price floor, staleness) have no
    band. The prior month's membership comes from the chain in membership().
    """
    me = pd.Timestamp(signal_asof)
    prev_ids = None
    if _hysteresis_on(cfg):
        prev = pidx.prev_month_end(me)
        prev_ids = membership(pidx, prev, cfg) if prev is not None else frozenset()
    out = screen_month(pidx, me, cfg, prev_ids)
    if _hysteresis_on(cfg) and me not in pidx.membership:
        pidx.membership[me] = frozenset(out.index)     # the chain reuses this month
    return out


def screen_month(pidx, me, cfg, prev_ids=None):
    """One month's screens given the prior month's members (None = no
    hysteresis: entry cuts only). build_universe() is the public entry."""
    u = cfg["universe"]
    me = pd.Timestamp(me)
    rows = pidx.month_rows(me)
    if rows is None or rows.empty:
        return pd.DataFrame()
    df = rows.set_index("ID").join(pidx.meta, how="left")
    stale = pd.Timedelta(days=int(u["max_price_staleness_days"]))
    df = df[(me - df["date"]) <= stale]
    if "exchange" in df.columns:
        df = df[df["exchange"].isin(list(u["exchanges"]))]
    if "category" in df.columns:
        df = df[df["category"].isin(list(u["categories"]))]
    df = df[df["px_unadj"].notna() & (df["px_unadj"] >= float(u["min_price_usd"]))]
    df = df[df["mkt_cap_usd"].notna() & df["adv_usd"].notna()]
    if df.empty:
        return df
    # RELATIVE screens, month by month. Size: the Fama-French microcap cut —
    # names below the configured percentile of the breakpoint exchange's
    # (NYSE) market caps THAT MONTH are out. Liquidity: the bottom
    # `adv_min_pctl` percent by dollar volume among the cap-screened names are
    # out. Both cuts move with the market, so the 1999 and 2025 universes are
    # defined the same way in relative terms.
    # With hysteresis a CURRENT member stays while at or above the exit
    # percentile; a non-member needs the entry percentile. Both cuts are
    # percentiles of the same reference cross-section (NYSE caps for size;
    # the cap-screened names for ADV), so the band is relative like the cuts.
    bp = u.get("size_breakpoint") or {}
    hyst = prev_ids is not None and _hysteresis_on(cfg)
    was_member = pd.Series(df.index.isin(list(prev_ids)) if hyst else False, index=df.index)
    size_cut = relative_size_cut(df, bp)
    size_exit = (relative_size_cut(df, dict(bp, pctl=bp["exit_pctl"]))
                 if hyst and size_cut is not None and bp.get("exit_pctl") is not None else None)
    # The ADV cuts are percentiles of the ENTRY-size-screened cross-section,
    # never of a set that already holds band-retained names: every threshold
    # is a function of the month's cross-section alone, and the band can
    # only ADD prior members, never move the bar for a new entrant.
    adv_ref = df[df["mkt_cap_usd"] >= size_cut] if size_cut is not None else df
    if size_cut is not None:
        keep = df["mkt_cap_usd"] >= size_cut
        if size_exit is not None:
            keep = keep | (was_member & (df["mkt_cap_usd"] >= size_exit))
        df = df[keep]
        was_member = was_member.loc[df.index]
    adv_pctl = float(u.get("adv_min_pctl", 0.0) or 0.0)
    adv_exit_pctl = float(u.get("adv_exit_pctl", 0.0) or 0.0)
    adv_cut = (float(adv_ref["adv_usd"].quantile(adv_pctl / 100.0))
               if adv_pctl > 0 and len(adv_ref) else None)
    adv_exit = (float(adv_ref["adv_usd"].quantile(adv_exit_pctl / 100.0))
                if hyst and adv_cut is not None and adv_exit_pctl > 0 else None)
    if adv_cut is not None:
        keep = df["adv_usd"] >= adv_cut
        if adv_exit is not None:
            keep = keep | (was_member & (df["adv_usd"] >= adv_exit))
        df = df[keep]
        was_member = was_member.loc[df.index]
    if df.empty:
        return df
    df = df.copy()
    df["size_cut_usd"] = float("nan") if size_cut is None else float(size_cut)
    df["adv_cut_usd"] = float("nan") if adv_cut is None else float(adv_cut)
    df["size_exit_cut_usd"] = float("nan") if size_exit is None else float(size_exit)
    df["adv_exit_cut_usd"] = float("nan") if adv_exit is None else float(adv_exit)
    # Retained only by the band: below an entry cut, kept as a prior member.
    below_entry = pd.Series(False, index=df.index)
    if size_cut is not None:
        below_entry |= df["mkt_cap_usd"] < size_cut
    if adv_cut is not None:
        below_entry |= df["adv_usd"] < adv_cut
    df["retained_by_band"] = (was_member & below_entry).astype(bool)
    df["region"] = u["region"]
    df["px_usd"] = df["px_unadj"].astype(float)
    df["adv_pctl_region"] = df.groupby("region")["adv_usd"].rank(pct=True, method="average") * 100
    df["liq_tier"] = df["adv_pctl_region"].apply(lambda p: _assign_tier_pctl(p, u["liquidity_tier_pctl"]))
    sec, ind = u.get("sector_field", "sector"), u.get("industry_field", "industry")
    df["sector"] = df[sec] if sec in df.columns else "UNKNOWN"
    df["industry_group"] = df[ind] if ind in df.columns else "UNKNOWN"
    keep = ["region", "liq_tier", "sector", "industry_group", "exchange", "category",
            "px_usd", "closeadj", "mkt_cap_usd", "adv_usd", "adv_pctl_region", "date",
            "size_cut_usd", "adv_cut_usd", "size_exit_cut_usd", "adv_exit_cut_usd",
            "retained_by_band"]
    keep = [c for c in keep if c in df.columns]
    return df[keep].sort_values("adv_usd", ascending=False)


def _skip1_base(pidx, universe, me1, ret_end, stale):
    """(p0, ret_base) for `return_start="skip1"`: the base price of the
    month-t+1 return is the adjusted close of the name's FIRST trade in the
    calendar month of `me1` (the first trading day after the signal date),
    when that trade is on or before `ret_end` and within the staleness window
    (`universe.max_price_staleness_days`, the same tolerance the window END
    uses) of the market's first trading day of the month (the earliest
    first trade of any SEP name that month). Otherwise the base falls back
    to the signal-date close, and the unchanged partial / gap / delisting
    branches of forward_returns() then apply exactly as in the default.
    ret_base: 'first_day' (base on the market's first trading day),
    'first_trade_late' (the name's first trade, after the market's first
    day but inside the tolerance), 'signal_close' (fallback)."""
    p_sig = universe["closeadj"].astype(float)
    first = pidx.first_trade_rows(me1)
    if first is None or first.empty:
        return p_sig, pd.Series("signal_close", index=universe.index, dtype=object)
    mkt_first = first["first_date"].min()
    f = first.reindex(universe.index)
    fd = f["first_date"]
    ok = (f["first_closeadj"].notna() & fd.notna() & (fd <= pd.Timestamp(ret_end))
          & ((fd - mkt_first) <= stale))
    p0 = f["first_closeadj"].astype(float).where(ok, p_sig)
    base = pd.Series("signal_close", index=universe.index, dtype=object)
    base[ok & (fd == mkt_first)] = "first_day"
    base[ok & (fd != mkt_first)] = "first_trade_late"
    return p0, base


def forward_returns(pidx, universe, signal_asof, ret_end, cfg, return_start="close"):
    """Total return from the signal-date close to the last trade on or before
    `ret_end`, with the delisting convention applied to names that stop
    trading inside the window.

    Returns a frame indexed by ID: monthly_ret, ret_kind in
    {full, partial_delisted_performance, partial_delisted_merger, partial_gap,
    no_trade}.

    `return_start` (diagnostic; run_test.py `--return-start`):
      'close' (default)  the base is the signal-date close, as always. This
                         path is the original code, line for line.
      'skip1'            the base is the close of the name's first trade in
                         month t+1 (_skip1_base); the END is unchanged (the
                         last trade on or before `ret_end`, the next
                         month-end close), and so are the staleness test and
                         the delisting convention. A name that delists ON
                         the first trading day has p1 == p0 (its first trade
                         is its last), a stale end, partial 0.0 and then the
                         configured delisting return; a name with no trade
                         in month t+1 at all (delisted on or before the
                         first trading day, or a gap) keeps the signal-close
                         base, so its return and ret_kind equal the
                         default's. The frame gains `ret_base`.
    What shifts under skip1 is `monthly_ret` and everything computed from it
    downstream: decile and long-short returns (raw and hedged), the market
    return M the hedge reads (analytics.universe_market_return is the
    cap-weighted mean of these same `monthly_ret`, weights = the signal-date
    `mkt_cap_usd`, unchanged), the trailing beta (estimated on the shifted LS
    and the shifted M, months t-36..t-1), the down-market and bull/bear
    states (also read off that M), the IC, ICIR, IC decay and tier stats.
    What does not shift: the universe, every signal, ranks, deciles, the
    weights of M, ret_kind, coverage and the month count.
    """
    r = cfg["returns"]["delisting"]
    stale = pd.Timedelta(days=int(cfg["universe"]["max_price_staleness_days"]))
    me0 = pd.Timestamp(signal_asof)
    me1 = to_bme([pd.Timestamp(ret_end)]).iloc[0]
    if return_start not in RETURN_START_MODES:
        raise ValueError(f"return_start {return_start!r} not in {RETURN_START_MODES}")
    base = None
    if return_start == "skip1":
        p0, base = _skip1_base(pidx, universe, me1, ret_end, stale)
    else:
        p0 = universe["closeadj"].astype(float)
    nxt = pidx.month_rows(me1)
    if nxt is None:
        nxt = pd.DataFrame(columns=["ID", "closeadj", "date"]).set_index("ID")
    else:
        nxt = nxt.set_index("ID")[["closeadj", "date"]]
    nxt = nxt.reindex(universe.index)
    p1 = nxt["closeadj"].astype(float)
    d1 = nxt["date"]

    # Case 1: a trade at (or within the staleness window of) the return-window end.
    full = p1.notna() & ((pd.Timestamp(ret_end) - d1) <= stale)
    ret = pd.Series(np.nan, index=universe.index, dtype=float)
    ret[full] = p1[full] / p0[full] - 1.0
    kind = pd.Series("full", index=universe.index, dtype=object)

    # Case 2: traded in the window but the last trade is stale, or never traded
    # in the window at all -> partial return to the last price (or 0.0), then
    # the delisting convention if the name has genuinely stopped trading.
    part = ~full
    p_last = p1.where(p1.notna(), p0)
    partial = p_last / p0 - 1.0
    dl = pidx.delist.reindex(universe.index)
    stopped = dl["delisted"].fillna(False).astype(bool) & (dl["last_trade"] <= pd.Timestamp(ret_end))
    perf = part & stopped & (dl["kind"] == "performance")
    merg = part & stopped & (dl["kind"] == "merger")
    gap = part & ~stopped
    ret[perf] = (1.0 + partial[perf]) * (1.0 + float(r["performance_return"])) - 1.0
    ret[merg] = (1.0 + partial[merg]) * (1.0 + float(r["other_return"])) - 1.0
    ret[gap] = partial[gap]
    kind[perf] = "partial_delisted_performance"
    kind[merg] = "partial_delisted_merger"
    kind[gap & p1.notna()] = "partial_gap"
    kind[gap & p1.isna()] = "no_trade"
    if base is not None:
        return pd.DataFrame({"monthly_ret": ret, "ret_kind": kind, "ret_base": base})
    return pd.DataFrame({"monthly_ret": ret, "ret_kind": kind})


# =============================================================================
# The per-month context a factor sees
# =============================================================================

def annual_window(signal_asof, anchor_month=6, publish_lag_months=1):
    """OSAP's annual, anchor-month estimation window (Hou-Moskowitz price
    delay: daily data from July of Y-1 through June of Y, first used at the
    July signal of Y and held until the next window is published).

    Returns (window_start, window_end), both inclusive, for the most recent
    window whose anchor month + `publish_lag_months` is on or before the
    signal's month: window_end = the last business day of that anchor month,
    window_start = the first calendar day of the month 11 months before it
    (so the window is 12 whole calendar months, whatever the leap year).
    Month arithmetic is on calendar-month periods, never day counts, so a
    June window is first usable at the July signal whatever day July's
    business month-end falls on. window_end <= signal always (a lag >= 0).
    """
    anchor_month = int(anchor_month)
    lag = int(publish_lag_months)
    if not 1 <= anchor_month <= 12 or lag < 0:
        raise ValueError("anchor_month in 1..12 and publish_lag_months >= 0")
    last_ok = pd.Timestamp(signal_asof).to_period("M") - lag
    year = last_ok.year if last_ok.month >= anchor_month else last_ok.year - 1
    end_p = pd.Period(year=year, month=anchor_month, freq="M")
    window_end = to_bme([end_p.end_time.normalize()]).iloc[0]
    window_start = (end_p - 11).start_time.normalize()
    return pd.Timestamp(window_start), pd.Timestamp(window_end)


class MonthContext:
    """Everything a factor may read for one signal date, and nothing later.

    Every accessor is bounded by `signal_asof`: fundamentals by filing date,
    prices by trade date. A factor cannot reach the holding month through this
    object, which is the blanket look-ahead guard the BQuant project got from
    its as_of_date parameter.
    """

    def __init__(self, snap, pidx, universe, signal_asof, cfg, sf1_cache):
        self.snap = snap
        self.pidx = pidx
        self.universe = universe
        self.signal_asof = pd.Timestamp(signal_asof)
        self.cfg = cfg
        self._sf1 = sf1_cache
        self.ids = universe.index
        self._mctx = None

    def _listed_at(self, me):
        """IDs with a trade in the business month ending `me` (a row in the
        monthly panel), OSAP's "the firm is in CRSP that month". Empty when
        the month is outside the panel."""
        me = pd.Timestamp(me)
        if me not in self.pidx.date_wide.columns:
            return pd.Index([], dtype=object)
        col = self.pidx.date_wide[me]
        return pd.Index(col.index[col.notna()].astype(str))

    def market_context(self):
        """This month's context over the MARKET instead of the screened
        universe: every common stock on a listed exchange
        (market_constituent_ids) that traded in the signal month. Every
        accessor works on it. For a signal OSAP standardises or averages
        across all of CRSP (an industry mean, an industry z-score, a
        cross-sectional regression): compute the raw values on
        ctx.market_context(), adjust across the market, then reindex to
        ctx.ids. The harness still scores only universe IDs (an
        alpha-review finding)."""
        if self._mctx is None:
            listed = self._listed_at(self.signal_asof)
            ids = self._scope_ids("market")
            ids = ids[ids.isin(listed)]
            frame = pd.DataFrame(index=pd.Index(ids, name=self.ids.name))
            self._mctx = MonthContext(self.snap, self.pidx, frame, self.signal_asof,
                                      self.cfg, self._sf1)
        return self._mctx

    def _scope_ids(self, scope):
        """IDs an accessor reads. "universe" (the default) is this month's
        screened universe. "market" is every common stock on a listed
        exchange, with no price, size or liquidity screen
        (market_constituent_ids, the same set as the market return): for
        cross-sectional aggregates OSAP builds over all of CRSP, such as an
        industry's total sales for a Herfindahl (an alpha-reviewer
        finding). Never a way to put a non-universe name in a sort:
        the harness scores only universe IDs."""
        if scope == "universe":
            return self.ids
        if scope == "market":
            ids = getattr(self.pidx, "_market_scope_ids", None)
            if ids is None:
                ids = pd.Index(sorted(str(i) for i in market_constituent_ids(self.snap, self.cfg)))
                self.pidx._market_scope_ids = ids
            return ids
        raise ValueError(f"scope must be 'universe' or 'market', not {scope!r}")

    # ---- fundamentals -----------------------------------------------------
    def _sf1_frame(self, dimension):
        if dimension in self._sf1:
            return self._sf1[dimension]
        sf1 = self.snap.table("SF1")
        sub = sf1[sf1["dimension"] == dimension].copy()
        sub["datekey"] = pd.to_datetime(sub["datekey"])
        sub["reportperiod"] = pd.to_datetime(sub["reportperiod"])
        sub["ID"] = sub["ticker"].map(self.snap.ticker_map("SF1"))
        sub = sub.dropna(subset=["ID"])
        # Sorted by datekey then reportperiod so that two filings on one day
        # resolve to the later period, and merge_asof's "last row wins" holds.
        sub = sub.sort_values(["datekey", "reportperiod"], kind="mergesort").reset_index(drop=True)
        self._sf1[dimension] = sub
        return sub

    def fundamentals(self, fields, lag_months=0, dimension=None):
        """Latest filing per ID with datekey <= signal_asof - lag_months,
        no older than max_fundamental_age_months. Frame indexed by ID with
        the requested fields plus datekey and reportperiod; NaN where no
        qualifying filing exists."""
        pit = self.cfg["point_in_time"]
        dim = dimension or pit["sf1_dimension"]
        sub = self._sf1_frame(dim)
        missing = [f for f in fields if f not in sub.columns]
        if missing:
            raise KeyError(f"SF1[{dim}] has no column(s) {missing}")
        target = (self.signal_asof - pd.DateOffset(months=int(lag_months))).normalize()
        left = pd.DataFrame({"ID": self.ids.astype(str),
                             "t": pd.Series([target] * len(self.ids), dtype="datetime64[ns]")})
        right = sub[["ID", "datekey", "reportperiod"] + list(fields)]
        tol = pd.Timedelta(days=int(round(30.4375 * float(pit["max_fundamental_age_months"]))))
        got = pd.merge_asof(left, right, left_on="t", right_on="datekey", by="ID",
                            direction="backward", tolerance=tol)
        return got.set_index("ID").drop(columns=["t"]).reindex(self.ids)

    def fundamentals_history(self, fields, n_periods, dimension=None):
        """The last `n_periods` filings per ID KNOWN at the signal date, as a
        long frame: ID, q_back (0 = latest, 1 = the one before, ...),
        reportperiod, datekey, fields. Point-in-time by construction: only
        rows with datekey <= signal_asof, so a restated quarter (later
        datekey) cannot replace the vintage that was public.

        For quarterly factors (dimension="ARQ") this is the right shape:
        aligning "the same quarter a year ago" by REPORT PERIOD rather than
        by an as-of date twelve months back, which lands on the wrong quarter
        ~15% of the time when filings are late or fiscal years shift. A name
        whose latest filing is older than max_fundamental_age_months gets no
        rows. Periods are deduplicated on reportperiod keeping the latest
        datekey (an amended filing before the signal supersedes the original).
        """
        pit = self.cfg["point_in_time"]
        dim = dimension or pit["sf1_dimension"]
        sub = self._sf1_frame(dim)
        missing = [f for f in fields if f not in sub.columns]
        if missing:
            raise KeyError(f"SF1[{dim}] has no column(s) {missing}")
        tol = pd.Timedelta(days=int(round(30.4375 * float(pit["max_fundamental_age_months"]))))
        known = sub[(sub["datekey"] <= self.signal_asof) & sub["ID"].isin(set(self.ids.astype(str)))]
        known = (known.sort_values(["ID", "reportperiod", "datekey"], kind="mergesort")
                      .drop_duplicates(["ID", "reportperiod"], keep="last"))
        last = known.groupby("ID")["datekey"].max()
        fresh = last[last >= self.signal_asof - tol].index
        known = known[known["ID"].isin(fresh)]
        hist = known.groupby("ID", sort=False).tail(int(n_periods)).copy()
        hist["q_back"] = (hist.groupby("ID")["reportperiod"].rank(ascending=False, method="first")
                          .astype(int) - 1)
        cols = ["ID", "q_back", "reportperiod", "datekey"] + list(fields)
        return hist[cols].sort_values(["ID", "q_back"]).reset_index(drop=True)

    def fundamentals_yoy(self, fields, years=1, dimension=None, tol_days=45):
        """The latest known filing and the filing for the SAME fiscal period
        `years` earlier, aligned by REPORT PERIOD, both as known at the
        signal. Frame indexed by ID: reportperiod, datekey, fields (latest)
        and reportperiod_lag, datekey_lag, <field>_lag (the period whose
        reportperiod is within `tol_days` of latest - `years`; the closest
        one when several qualify). NaN where the latest filing is older than
        max_fundamental_age_months or no year-ago period is known.

        `fundamentals(lag_months=12)` returns "the latest filing known twelve
        months ago", which is the wrong quarter ~15% of the time (late or
        shifted filings), so a year-over-year change built from it runs over
        9 or 15 months while a TTM flow runs over 12, and a filing that is
        stale at both dates yields a zero change. Added after alpha-review of
        the first translated inventory batch (Accruals).
        """
        cols = ["reportperiod", "datekey"] + list(fields)
        lag_cols = [f"{c}_lag" for c in cols]
        out = pd.DataFrame(index=self.ids, columns=cols + lag_cols, dtype=float)
        h = self.fundamentals_history(fields, n_periods=4 * int(years) + 4, dimension=dimension)
        if h.empty:
            out[["reportperiod", "datekey", "reportperiod_lag", "datekey_lag"]] = pd.NaT
            return out
        cur = h[h["q_back"] == 0].set_index("ID")[cols]
        target = cur["reportperiod"] - pd.DateOffset(years=int(years))
        past = h[h["q_back"] > 0].merge(target.rename("target"), left_on="ID", right_index=True)
        past["gap"] = (past["reportperiod"] - past["target"]).abs()
        past = past[past["gap"] <= pd.Timedelta(days=int(tol_days))]
        past = (past.sort_values(["ID", "gap", "q_back"], kind="mergesort")
                    .drop_duplicates("ID", keep="first").set_index("ID")[cols])
        past.columns = lag_cols
        got = cur.join(past, how="left")
        return got.reindex(self.ids)

    def fundamentals_at_month_ends(self, fields, months_back_list, dimension=None, scope="universe"):
        """`fundamentals` as known at many trailing month-ends, from one
        merge. Long frame with columns ID, months_back, reportperiod, datekey,
        fields: per universe ID and lag m, the latest filing with datekey <=
        the BUSINESS month-end m months before the signal (to_bme, the same
        target rule as at_month_end) and no older than
        max_fundamental_age_months before that month-end. (ID, lag) pairs with
        no qualifying filing are absent. Lag 0 is the signal date itself (a
        business month-end), so lag 0 equals `fundamentals(fields)`.

        Each lag sees only what was public at its own month-end: a filing (or
        restatement) with a later datekey cannot reach an earlier lag. The
        latest filing is carried forward between filings, exactly as a
        monthly as-of panel would. Added after a candidate had hand-rolled
        this merge_asof over 60 month-ends (alpha-reviewer).
        `scope="market"` reads every listed common stock (see _scope_ids),
        and at each lag only those that traded in that lag's month.
        """
        pit = self.cfg["point_in_time"]
        dim = dimension or pit["sf1_dimension"]
        sub = self._sf1_frame(dim)
        missing = [f for f in fields if f not in sub.columns]
        if missing:
            raise KeyError(f"SF1[{dim}] has no column(s) {missing}")
        cols = ["ID", "months_back", "reportperiod", "datekey"] + list(fields)
        lags = sorted({int(m) for m in months_back_list})
        scope_ids = self._scope_ids(scope)
        if not lags or len(scope_ids) == 0:
            return pd.DataFrame(columns=cols)
        targets = to_bme([(self.signal_asof - pd.DateOffset(months=m)).normalize()
                          for m in lags]).to_numpy()
        ids = scope_ids.astype(str)
        if scope == "market":
            # Per lag, only names that traded in that lag's month: a firm that
            # has stopped trading does not count in an aggregate just because
            # its last filing is under max_fundamental_age_months old
            # (alpha-review; OSAP's SignalMasterTable row rule).
            parts = []
            for m, t in zip(lags, targets):
                listed = self._listed_at(t)
                keep = ids[ids.isin(listed)]
                parts.append(pd.DataFrame({"ID": np.asarray(keep), "months_back": m,
                                           "t": pd.Timestamp(t)}))
            left = pd.concat(parts, ignore_index=True)
            left["t"] = pd.to_datetime(left["t"])
            left = left.sort_values("t", kind="mergesort")
            if left.empty:
                return pd.DataFrame(columns=cols)
        else:
            left = pd.DataFrame({
                "ID": np.tile(np.asarray(ids), len(lags)),
                "months_back": np.repeat(lags, len(ids)),
                "t": pd.to_datetime(np.repeat(targets, len(ids))),
            }).sort_values("t", kind="mergesort")
        right = sub[["ID", "datekey", "reportperiod"] + list(fields)]
        tol = pd.Timedelta(days=int(round(30.4375 * float(pit["max_fundamental_age_months"]))))
        got = pd.merge_asof(left, right, left_on="t", right_on="datekey", by="ID",
                            direction="backward", tolerance=tol)
        got = got.dropna(subset=["datekey"])
        return got[cols].sort_values(["ID", "months_back"]).reset_index(drop=True)

    # ---- static ticker metadata ---------------------------------------------
    def ticker_meta(self, fields, scope="universe"):
        """TICKERS columns for the universe IDs (siccode, sector, industry,
        exchange, category ...). These are the vendor's CURRENT classifications,
        not historical ones — a firm reclassified in 2015 carries its 2015 code
        in 1999. Acceptable for a sample restriction that OSAP itself applies
        on a current header code (a financials SIC 6000-6999 screen); never for a
        signal value. Declare each as `TICKERS.<field>` in FactorDef.inputs.
        `scope="market"` returns the same fields for every listed common
        stock, for grouping a market-scope aggregate (see _scope_ids)."""
        meta = self.pidx.meta
        missing = [f for f in fields if f not in meta.columns]
        if missing:
            raise KeyError(f"TICKERS has no column(s) {missing}")
        return meta[list(fields)].reindex(self._scope_ids(scope))

    # ---- prices -------------------------------------------------------------
    def monthly_closeadj(self, months_back):
        """Wide frame: index ID (universe), columns = the business month-ends
        from the BUSINESS month-end `months_back` months before the signal, to
        the signal, inclusive; closeadj at each.

        The lower bound is a business month-end on purpose. Filtering on the
        raw calendar date (signal - N months) excluded the window's first
        column whenever that calendar date fell on a weekend after the
        business month-end — 2001-12-31 minus 12 months is Sunday 2000-12-31,
        and December 2000's business month-end is the 29th — so a 12-month
        momentum went NaN for every name in ~22% of months and the composite
        silently ran on four legs. Caught on the first baseline run
        (research/results/001, never logged) by the leg-coverage table.
        """
        lo = to_bme([(self.signal_asof - pd.DateOffset(months=int(months_back))).normalize()]).iloc[0]
        cols = [m for m in self.pidx.months if lo <= m <= self.signal_asof]
        return self.pidx.close_wide.reindex(index=self.ids, columns=cols)

    def has_price_at(self, months_back, tolerance_days=7):
        """True for each universe ID with a trade within `tolerance_days`
        calendar days ON OR BEFORE the business month-end `months_back` months
        before the signal. The history gate."""
        target = to_bme([(self.signal_asof - pd.DateOffset(months=int(months_back))).normalize()]).iloc[0]
        if target not in self.pidx.date_wide.columns:
            return pd.Series(False, index=self.ids)
        d = self.pidx.date_wide.reindex(index=self.ids)[target]
        return d.notna() & ((target - d) <= pd.Timedelta(days=int(tolerance_days)))

    def at_month_end(self, table, fields, months_back, tolerance_days=7, scope="universe"):
        """Per universe ID, the last `table` row (SEP or DAILY) ON OR BEFORE
        the BUSINESS month-end `months_back` months before the signal and no
        more than `tolerance_days` calendar days earlier than it. Frame
        indexed by ID with `fields` plus `date` (the trade date read); NaN
        where no row qualifies. The same target and tolerance as
        has_price_at, for a lagged series that is not closeadj (a share count
        from marketcap/close, an unadjusted price). Added after a candidate
        had rolled its own calendar-date snap inside the factor.

        `scope="market"` reads every listed common stock (see _scope_ids)
        and indexes the result by those that TRADED IN THE TARGET MONTH
        (_listed_at, OSAP's "in CRSP that month"), so a firm alive at the
        lag but dead by the signal is in, and one not yet listed or already
        gone is not — no survivorship in a market-wide pooled sample.
        """
        target = to_bme([(self.signal_asof - pd.DateOffset(months=int(months_back))).normalize()]).iloc[0]
        days_back = (self.signal_asof - target).days + int(tolerance_days) + 1
        d = self.daily(table, fields, days_back, scope=scope)
        d = d[(d["date"] <= target) & (d["date"] >= target - pd.Timedelta(days=int(tolerance_days)))]
        last = d.sort_values(["ID", "date"], kind="mergesort").groupby("ID").tail(1)
        if scope == "market":
            ids = self._scope_ids(scope)
            ids = ids[ids.isin(self._listed_at(target))]
            return last.set_index("ID")[list(fields) + ["date"]].reindex(ids)
        return last.set_index("ID")[list(fields) + ["date"]].reindex(self.ids)

    def at_month_ends(self, table, fields, months_back_list, tolerance_days=7, scope="universe"):
        """at_month_end for many lags from ONE daily pull. Long frame with
        columns ID, months_back, date, fields: per ID and lag, the last row
        on or before that lag's business month-end and within
        `tolerance_days` of it; (ID, lag) pairs with no such row are absent.
        Added after a candidate whose 36 lags x 2 tables of single
        at_month_end calls each re-read the table (alpha-reviewer).
        `scope="market"` reads every listed common stock and, at each lag,
        keeps only those that traded in that lag's month (_listed_at), as
        fundamentals_at_month_ends does: a firm that has since died is in
        the lags when it was alive (Frontier's pooled 60-month regression).
        """
        lags = sorted({int(m) for m in months_back_list})
        targets = {m: to_bme([(self.signal_asof - pd.DateOffset(months=m)).normalize()]).iloc[0]
                   for m in lags}
        tol = pd.Timedelta(days=int(tolerance_days))
        days_back = (self.signal_asof - min(targets.values())).days + int(tolerance_days) + 1
        d = self.daily(table, fields, days_back, scope=scope).sort_values(["ID", "date"], kind="mergesort")
        out = []
        for m, t in targets.items():
            w = d[(d["date"] <= t) & (d["date"] >= t - tol)]
            if scope == "market":
                w = w[w["ID"].isin(self._listed_at(t))]
            last = w.groupby("ID", sort=False).tail(1).copy()
            last["months_back"] = m
            out.append(last)
        cols = ["ID", "months_back", "date"] + list(fields)
        if not out:
            return pd.DataFrame(columns=cols)
        return pd.concat(out, ignore_index=True)[cols]

    def daily(self, table, fields, days_back, scope="universe"):
        """Long frame of `table` rows for universe IDs with signal - days_back
        < date <= signal. SEP or DAILY. `scope="market"` returns the rows of
        every listed common stock (market_constituent_ids, see _scope_ids),
        alive or since delisted: a row exists only on a day the name traded,
        so no listing mask is needed (TrendFactor's all-stock moving
        averages, pooled daily cross-sections). The harness still scores
        only universe IDs."""
        ids = self._scope_ids(scope)
        cols = ["ticker", "date"] + [f for f in fields if f not in ("ticker", "date")]
        df = self.snap.table(table, cols)
        start = self.signal_asof - pd.Timedelta(days=int(days_back))
        d = pd.to_datetime(df["date"])
        m = (d > start) & (d <= self.signal_asof)
        out = df.loc[m].copy()
        out["date"] = d[m]
        out["ID"] = out["ticker"].map(self.snap.ticker_map(table))
        return out[out["ID"].isin(set(ids))].drop(columns=["ticker"])

    def partial_months(self, table="SEP"):
        """Calendar months (pd.Period, freq "M") in which `table` holds only
        part of the month's trading days because the snapshot starts inside
        it: the month of the table's first date when that date is later than
        the month's first business day. On this snapshot SEP starts
        1997-12-31, so 1997-12 is a one-day stub. A factor that aggregates
        daily rows into calendar months drops these months rather than
        hard-coding a date (alpha-review 2026-09-26). Computed once per
        snapshot and table; independent of the signal date."""
        cache = self.snap.__dict__.setdefault("_partial_months", {})
        if table not in cache:
            d = pd.to_datetime(self.snap.table(table, ["date"], keep=False)["date"])
            first = d.min()
            out = frozenset()
            if pd.notna(first):
                month_first_bday = pd.offsets.BMonthBegin().rollback(first.normalize())
                if first.normalize() > month_first_bday:
                    out = frozenset({first.to_period("M")})
            cache[table] = out
        return cache[table]

    def market_daily(self, days_back, with_names=False, min_days=None, col="vw"):
        """The daily market return for signal - days_back < date <= signal
        (the same bounds as `daily`): a Series indexed by date — `mkt_ret`
        (col="vw", value-weighted, the default) or `ew_ret` (col="ew", the
        equal-weighted mean of the SAME name-days: CRSP ewretd analogue) —
        or with `with_names=True` a frame with that column and n_names
        (constituents that day).

        COVERAGE: the series starts 1998-12-02 (DAILY.marketcap starts
        1998-12-01 — a data limit), so a window reaching before that is
        THIN, not wrong: a 252-day beta at the 1999-01 signal has ~20 days.
        Pass `min_days`: when fewer than that many market days fall in the
        window, the result is EMPTY and the factor must treat the month as
        unscorable. With min_days=None the window is returned as is, and
        the factor owns the check.

        CRSP-like all-stock market (see build_market_daily): common stock on
        the universe's exchanges, NO size/price/ADV screen, weights = the
        PRIOR trading day's DAILY.marketcap. Bad prints are dropped
        CAUSALLY: a name-day with r > +100% or r < -80% is dropped on its
        own, the next day is dropped when it reverses that spike, any other
        |r| > 500% is dropped, and a weight above 1e5 x the name's trailing
        20-row median dollar volume is dropped as an implausible cap. No
        value on date d reads anything after d. It is a RAW return, not
        mktrf: the snapshot holds no risk-free rate. For betas / covariances
        / residuals over daily windows the near-constant rf is immaterial; a
        factor using this in place of OSAP's mktrf declares that deviation,
        and also that returns across a name's trading gap, delisting returns
        and genuine >+100% days are NOT in the series (CRSP includes them).
        The EW series weights every constituent name-day equally, so those
        exclusions matter more for it than for VW. Declare `SEP.closeadj`
        and `DAILY.marketcap` in FactorDef.inputs."""
        cols = {"vw": "mkt_ret", "ew": "ew_ret"}
        if col not in cols:
            raise ValueError(f"market_daily col must be one of {sorted(cols)}, got {col!r}")
        c = cols[col]
        m = self.pidx.market()
        start = self.signal_asof - pd.Timedelta(days=int(days_back))
        idx = pd.DatetimeIndex(m.index)
        w = m.loc[(idx > start) & (idx <= self.signal_asof)]
        if min_days is not None and len(w) < int(min_days):
            w = w.iloc[0:0]
        if with_names:
            return w[[c, "n_names"]].copy()
        return w[c].copy()

    def monthly_market(self, months_back, col="vw", min_days=15):
        """The monthly market return for the `months_back` business months
        ending at the signal month, compounded from the guarded daily series
        (`market_daily`: same constituents, prior-day cap weights for "vw",
        the same name-days equally weighted for "ew", the same causal
        bad-print and implausible-cap guards). A Series indexed by business
        month-end, ascending, length `months_back`; a month with fewer than
        `min_days` market days is NaN, and so is the month holding the
        series' first day (1998-12, which lacks its first trading day): never
        a partial compounding. Month m is the days in
        (BME(m-1), BME(m)], the same span as a monthly_closeadj return, so a
        regression of a stock's monthly return on this series lines up.
        RAW, not excess (no rf in the snapshot). Added for monthly betas and
        comoments after alpha-review found an in-factor EW aggregate of raw
        month-end closes with none of these guards (Beta, FETCH-02).
        Declare `SEP.closeadj` and `DAILY.marketcap` in FactorDef.inputs."""
        cols = {"vw": "mkt_ret", "ew": "ew_ret"}
        if col not in cols:
            raise ValueError(f"monthly_market col must be one of {sorted(cols)}, got {col!r}")
        m = self.pidx.market()[cols[col]]
        m = m[pd.DatetimeIndex(m.index) <= self.signal_asof]
        months = to_bme([(self.signal_asof - pd.DateOffset(months=k)).normalize()
                         for k in range(int(months_back) - 1, -1, -1)])
        months = pd.DatetimeIndex(months)
        if m.empty:
            return pd.Series(np.nan, index=months, name=cols[col])
        key = pd.DatetimeIndex(to_bme(m.index).to_numpy())
        g = (1.0 + m.astype(float)).groupby(key)
        ret = g.prod() - 1.0
        n = g.size()
        ret = ret.where(n >= int(min_days))
        # The month holding the series' first day is partial by construction
        # (1998-12 lacks its first trading day): blank it rather than compound
        # part of a month against a full-month stock return.
        first = pd.DatetimeIndex(to_bme([self.pidx.market().index.min()]).to_numpy())[0]
        ret = ret[ret.index != first]
        return ret.reindex(months).rename(cols[col])

    def ff3_daily(self, days_back, min_days=None):
        """Daily Fama-French three factors for signal - days_back < date <=
        signal (market_daily's bounds): a frame indexed by date with columns
        mkt, smb, hml. Only COMPLETE rows are served — smb / hml start the
        first trading day after the June 1999 formation (the first June with
        a December 1998 cap), so a window reaching before that is THIN.
        `min_days` as in market_daily: fewer complete days than that and the
        result is EMPTY (the month is unscorable).

        Built by build_ff3_daily on the market's own name-days (same
        constituents, calendar, prior-day cap weights and causal bad-print
        guards; `mkt` IS market_daily's value-weighted series): June 2x3
        sorts on NYSE size median and 30/70 NYSE B/M percentiles, BE from SF1
        ARY for the fiscal year ending in calendar y-1 with datekey <= the
        June formation date, ME for B/M = December y-1 cap, held July y to
        June y+1. No value on date d reads anything after d. DECLARED
        DEVIATIONS for a factor using it in place of Ken French's factors:
        mkt is a RAW return, not Mkt-RF (no risk-free rate is held; SMB and
        HML are long-short, so rf cancels in them); CURRENT TICKERS exchange
        for the NYSE breakpoints; BE = equity + taxliabilities with no
        preferred stock; no delisting returns. Declare `SEP.closeadj`,
        `DAILY.marketcap`, `SF1.equity`, `SF1.assets`, `SF1.liabilities`
        and `SF1.taxliabilities` in FactorDef.inputs."""
        f = self.pidx.ff3()
        start = self.signal_asof - pd.Timedelta(days=int(days_back))
        idx = pd.DatetimeIndex(f.index)
        w = f.loc[(idx > start) & (idx <= self.signal_asof), ["mkt", "smb", "hml"]].dropna()
        if min_days is not None and len(w) < int(min_days):
            w = w.iloc[0:0]
        return w.copy()

    def monthly_ff3(self, months_back, min_days=15):
        """Monthly Fama-French three factors for the `months_back` business
        months ending at the signal month, from the daily build
        (build_ff3_daily): a frame indexed by business month-end, ascending,
        columns mkt, smb, hml. Month m is the days in (BME(m-1), BME(m)],
        monthly_market's span.

        mkt = the compounded daily VW market (monthly_market's number). SMB
        and HML are formed from MONTHLY PORTFOLIO returns, as Ken French's
        monthly factors are: each of the six portfolios' daily returns is
        compounded over the month, then SMB = mean(SL, SM, SH) - mean(BL, BM,
        BH) and HML = mean(SH, BH) - mean(SL, BL) — not the compounded daily
        SMB / HML, which is a different number. (Daily prior-day-cap weights
        compounded equal a buy-and-hold monthly VW return up to the guarded
        name-days.)

        Guards, as monthly_market: a month with fewer than `min_days` market
        days is NaN; the month holding the series' first day (1998-12) is
        NaN; smb / hml are NaN for a month in which any market day lacks the
        portfolio returns (the months before the first July after the first
        June formation). RAW mkt, not Mkt-RF. Declare the inputs listed in
        ff3_daily."""
        f = self.pidx.ff3()
        f = f[pd.DatetimeIndex(f.index) <= self.signal_asof]
        months = pd.DatetimeIndex(to_bme([(self.signal_asof - pd.DateOffset(months=k)).normalize()
                                          for k in range(int(months_back) - 1, -1, -1)]))
        out = pd.DataFrame(np.nan, index=months, columns=["mkt", "smb", "hml"])
        if f.empty:
            return out
        key = pd.DatetimeIndex(to_bme(f.index).to_numpy())
        ports = [f"r_{p}" for p in FF3_PORTS]
        x = (1.0 + f[["mkt"] + ports].astype(float))
        g = x.groupby(key)
        ret = g.prod(min_count=1) - 1.0
        n = g.size()
        complete = f[ports].notna().all(axis=1).groupby(key).all()
        ok = n >= int(min_days)
        first = pd.DatetimeIndex(to_bme([self.pidx.ff3().index.min()]).to_numpy())[0]
        ok &= ret.index != first
        r = {p: ret[f"r_{p}"].where(ok & complete) for p in FF3_PORTS}
        m = pd.DataFrame({"mkt": ret["mkt"].where(ok),
                          "smb": (r["SL"] + r["SM"] + r["SH"]) / 3 - (r["BL"] + r["BM"] + r["BH"]) / 3,
                          "hml": (r["SH"] + r["BH"]) / 2 - (r["SL"] + r["BL"]) / 2})
        return m.reindex(months)

    def _monthly_series(self, frame, col, months_back):
        """`col` of a monthly frame indexed by business month-end, over the
        `months_back` business month-ends ending at the signal month
        (monthly_market's month list), ascending; NaN where undefined. Rows
        after the signal are cut BEFORE the reindex, so no later month can
        be served."""
        s = frame[col]
        s = s[pd.DatetimeIndex(s.index) <= self.signal_asof]
        months = pd.DatetimeIndex(to_bme([(self.signal_asof - pd.DateOffset(months=k)).normalize()
                                          for k in range(int(months_back) - 1, -1, -1)]))
        return s.reindex(months).astype(float).rename(col)

    def monthly_ps_innov(self, months_back, refit=False):
        """The Pastor-Stambaugh aggregate liquidity innovation for the
        `months_back` business months ending at the signal month: a Series
        indexed by business month-end, ascending; NaN before the series is
        defined (the expanding AR fit needs PS_MIN_MONTHS months, so the
        first value is ~2001-02 on this snapshot). A causal REBUILD, not PS's
        published series (build_ps_innov_monthly): daily per-stock gamma on
        NYSE/AMEX common stock priced $5-$1000, value-scaled mean change, and
        the residual of the AR regression.

        refit=False (default): each month's residual under the coefficients
        fit through THAT month (an expanding window; fixed once written).
        refit=True: one fit through the SIGNAL month, and every month's
        residual under it (PS's full-sample shape, as of the signal):
        re-computed per signal from the cached monthly rows <= the signal
        (ps_refit_residuals), so it reads nothing later; the last value is
        the same either way.

        DECLARED DEVIATIONS for a factor using it: exchange as of t-1 per
        PS_EXCHANGE_RULE; current TICKERS category; no delisting returns, no
        gap returns, r < -80% / > +100% and no-trade days dropped; the AR fit
        is not PS's full sample; m_1 = the first defined month (a constant
        scale, rank-neutral for a beta). Declare `SEP.closeadj`, `SEP.close`,
        `SEP.volume`, `SEP.closeunadj`, `DAILY.marketcap` and
        `ACTIONS.contraname` in FactorDef.inputs."""
        if not refit:
            return self._monthly_series(self.pidx.ps(), "ps_innov", months_back)
        f = self.pidx.ps()
        f = f[pd.DatetimeIndex(f.index) <= self.signal_asof]
        res = ps_refit_residuals(f).to_frame("ps_innov")
        return self._monthly_series(res, "ps_innov", months_back)

    def monthly_tailex(self, months_back):
        """Kelly-Jiang's monthly tail-risk factor for the `months_back`
        business months ending at the signal month: a Series indexed by
        business month-end, ascending; NaN where undefined (the snapshot's
        first, partial month; a month with < TAIL_MIN_DAYS pooled days).
        tailex_m = mean log(r / retp5_m) over the pooled daily returns of
        every market constituent with r <= retp5_m, the "lower" 5th
        percentile (build_tailex_monthly). DECLARED DEVIATIONS: the pool is
        common stock on listed exchanges, not all of CRSP; the market's
        bad-print guards DROP r < -80% (measured on DATA_SHA 52402f7d1f9c,
        1999-2022: |tailex - tailex_unguarded| mean 0.0008, max 0.0057 in
        2003-10, tailex std 0.059; the cached frame carries both);
        no delisting returns; no-trade days dropped, the next day's two-day
        return kept. Declare `SEP.closeadj` and `SEP.volume` in
        FactorDef.inputs."""
        return self._monthly_series(self.pidx.tailex(), "tailex", months_back)

    def monthly_trend_coefs(self, months_back=1, which="ebar"):
        """Han-Zhou-Zhu trend coefficients for the `months_back` business
        months ending at the signal month: a frame indexed by business
        month-end, ascending, columns const, A_3 .. A_1000 (TREND_LAGS) plus
        n_obs, n_betas, ma_full, ebar_full. which="ebar" (default): the
        trailing TREND_BETA_WINDOW-month mean of the monthly slopes, ebar_t
        = mean(beta_{t-11} .. beta_t) — OSAP's EBeta for signal month t;
        which="beta": the month's own slopes (diagnostic). beta_m regresses
        the month-m return on the A_L at m-1 over OSAP's sample (fit(m-1)
        AND fit(m)), so every value in row t is known at BME(t); rows after
        the signal are cut BEFORE the reindex. NaN before the series starts
        (first beta/ebar 1999-01 on this snapshot: DAILY.marketcap starts
        1998-12). The trend value is sum_L ebar_L x A_L (NO intercept):
        take A_L from trend_ma_signals().

        CENSORING: `ebar_full` is False while any beta in the window was fit
        on A_L truncated by the SEP data start (1997-12-31; measured on
        DATA_SHA 52402f7d1f9c: A_1000 first complete at 2001-12-31, n_cal
        1005, so the first beta on full windows is 2002-01 and the first
        full-window ebar is 2002-12, used by the 2003-01 holding month);
        before that the long-lag columns were collinear or near-collinear and
        their coefficients are 0 or offsetting. A factor that scores those
        months declares it (spec sec. 8).

        DECLARED DEVIATIONS (build_trend_monthly's block comment): exchange
        in force per PS_EXCHANGE_RULE, CURRENT category for share codes;
        DAILY.marketcap per permaticker for mve_c; no delisting returns; raw
        closeadj monthly returns; SEP no-trade rows for CRSP midpoints;
        data-start censoring. Declare `SEP.close`, `SEP.closeadj`,
        `SEP.closeunadj`, `SEP.volume`, `DAILY.marketcap` and
        `ACTIONS.contraname` in FactorDef.inputs."""
        if which not in ("ebar", "beta"):
            raise ValueError(f"which must be 'ebar' or 'beta', not {which!r}")
        pre = "ebar_" if which == "ebar" else "b_"
        names = ["const"] + trend_ma_cols()
        f = self.pidx.trend()
        f = f[pd.DatetimeIndex(f.index) <= self.signal_asof]
        months = pd.DatetimeIndex(to_bme([(self.signal_asof - pd.DateOffset(months=k)).normalize()
                                          for k in range(int(months_back) - 1, -1, -1)]))
        out = f[[pre + c for c in names]].astype(float)
        out.columns = names
        for c in ("n_obs", "n_betas"):
            out[c] = f[c].astype(float)
        for c in ("ma_full", "ebar_full"):
            out[c] = f[c].astype(object)
        out = out.reindex(months)
        for c in ("ma_full", "ebar_full"):
            out[c] = out[c].where(out[c].notna(), False).astype(bool)
        return out

    def trend_ma_signals(self, scope="universe", tolerance_days=None):
        """The Han-Zhou-Zhu normalised moving averages at the signal: a frame
        indexed by this context's IDs (scope "universe") or the listed market
        names (scope "market", see _scope_ids), columns date (the name's last
        SEP row), n_rows and A_3 .. A_1000: A_L = mean(SEP.close over the
        name's last L rows, fewer when fewer exist) / close on that row
        (trend_ma_signals, the function the coefficient builder uses — the
        two see the same numbers). Reads SEP rows with signal - TREND_DAYS_BACK
        < date <= signal (`daily`); NaN for a name whose last row is more than
        `tolerance_days` (default TREND_TOL_DAYS) before the
        signal. With TREND_DAYS_BACK = 1800 calendar days the read holds
        ~1,240 trading days, so A_1000 equals the builder's for every name
        that has not missed more than ~240 trading days in the window; a
        name with fewer rows gets a partial window, as OSAP (min_samples=1).
        Declare `SEP.close` in FactorDef.inputs."""
        tol = TREND_TOL_DAYS if tolerance_days is None else int(tolerance_days)
        acols = trend_ma_cols()
        ids = self._scope_ids(scope)
        if scope == "market":
            ids = ids[ids.isin(self._listed_at(self.signal_asof))]
        d = self.daily("SEP", ["close"], TREND_DAYS_BACK, scope=scope)
        d = d[d["ID"].isin(set(ids))]
        ma = trend_ma_signals(d)
        me = to_bme([self.signal_asof]).iloc[0]
        ma = ma[(pd.DatetimeIndex(ma["month"]) == me)
                & (pd.to_datetime(ma["date"]) >= self.signal_asof - pd.Timedelta(days=tol))]
        return ma.set_index("ID")[["date", "n_rows"] + acols].reindex(pd.Index(ids, name=self.ids.name))

    def annual_window(self, anchor_month=6, publish_lag_months=1):
        """(window_start, window_end) of the most recent annual estimation
        window usable at this signal; see `annual_window`."""
        return annual_window(self.signal_asof, anchor_month, publish_lag_months)

    # ---- corporate actions and material events (HX-3) -----------------------
    def actions(self, kinds, months_back, fields=("value",)):
        """Long frame of ACTIONS rows for universe IDs, strictly before the
        signal: signal - months_back < date <= signal, `action` in `kinds`.

        ACTIONS spans 1997-12 and carries dividends (553k rows), initiations,
        splits, acquisitions and listings/delistings. It was loaded only for
        the delisting convention, so the whole dividend/event predictor family
        (DivInit, DivOmit, DivSeason, DivYieldST, ShareRepurchase, Spinoff,
        ExchSwitch) had no source it could reach. Rows are events, not a panel:
        a name with no action in the window is simply absent, which is the
        factor's business to interpret — absence of a dividend record is not a
        zero dividend, and a factor that treats it as one is manufacturing a
        mass point. Declare each as `ACTIONS.<field>` in FactorDef.inputs.
        """
        if isinstance(kinds, str):
            kinds = (kinds,)
        cols = ["ticker", "date", "action"] + [f for f in fields
                                               if f not in ("ticker", "date", "action")]
        df = self.snap.table("ACTIONS", cols)
        d = pd.to_datetime(df["date"])
        start = self.signal_asof - pd.DateOffset(months=int(months_back))
        m = (d > start) & (d <= self.signal_asof) & df["action"].isin(list(kinds))
        out = df.loc[m].copy()
        out["date"] = d[m]
        out["ID"] = out["ticker"].map(self.snap.ticker_map("ACTIONS"))
        return out[out["ID"].isin(set(self.ids))].drop(columns=["ticker"])

    def events(self, months_back):
        """Long frame of EVENTS rows (ID, date, eventcodes) for universe IDs,
        strictly before the signal. EVENTS spans 1993-11; `eventcodes` is a
        pipe-separated list of SEC 8-K item numbers, so a factor filters it
        itself rather than the harness guessing which codes matter.
        Declare `EVENTS.eventcodes` in FactorDef.inputs.
        """
        df = self.snap.table("EVENTS", ["ticker", "date", "eventcodes"])
        d = pd.to_datetime(df["date"])
        start = self.signal_asof - pd.DateOffset(months=int(months_back))
        m = (d > start) & (d <= self.signal_asof)
        out = df.loc[m].copy()
        out["date"] = d[m]
        out["ID"] = out["ticker"].map(self.snap.ticker_map("EVENTS"))
        return out[out["ID"].isin(set(self.ids))].drop(columns=["ticker"])


# =============================================================================
# One month, end to end
# =============================================================================

AUDIT_BASE_COLS = ["ID", "DATE", "DECILE", "COMPOSITE_SCORE", "monthly_ret",
                   "ret_kind", "RET_START", "RET_END", "SIGNAL_ASOF", "region",
                   "liq_tier", "sector", "mkt_cap_usd", "adv_usd"]


def compute_month_frame(snap, pidx, sf1_cache, factors, reb_dt, signal_asof,
                        ret_start, ret_end, cfg, return_start="close"):
    """Universe + every factor's raw column + forward return, for one month.

    Returns the un-scored frame (no COMPOSITE_SCORE / DECILE yet) so a Stage 2
    ladder can score many arms off one computation. None if the month has no
    universe or no returns.

    `return_start="skip1"` (diagnostic, forward_returns) puts the skip-a-day
    return in `monthly_ret` and ALSO carries the default signal-close return
    as `monthly_ret_close` and the base used as `RET_BASE`, so one run can
    pair the two on identical universes and scores. The default adds
    neither column.
    """
    univ = build_universe(pidx, signal_asof, cfg)
    if univ.empty:
        return None
    ctx = MonthContext(snap, pidx, univ, signal_asof, cfg, sf1_cache)
    df = univ.copy()
    df.index.name = "ID"
    for f in factors:
        s = f.compute(ctx)
        s = pd.to_numeric(pd.Series(s).reindex(df.index), errors="coerce")
        if f.history_months is not None:
            gate = ctx.has_price_at(f.history_months)
            s = s.where(gate)
        df[f.col] = s.astype(float)
    fr = forward_returns(pidx, univ, signal_asof, ret_end, cfg)
    if return_start != "close":
        fr_close = fr
        fr = forward_returns(pidx, univ, signal_asof, ret_end, cfg, return_start=return_start)
    df["monthly_ret"] = fr["monthly_ret"]
    df["ret_kind"] = fr["ret_kind"]
    if return_start != "close":
        df["monthly_ret_close"] = fr_close["monthly_ret"]
        df["RET_BASE"] = fr["ret_base"]
    df["DATE"] = pd.Timestamp(ret_end)
    df["RET_START"] = pd.Timestamp(ret_start)
    df["RET_END"] = pd.Timestamp(ret_end)
    df["SIGNAL_ASOF"] = pd.Timestamp(signal_asof)
    df["REB_DT"] = pd.Timestamp(reb_dt)
    return df.reset_index()
