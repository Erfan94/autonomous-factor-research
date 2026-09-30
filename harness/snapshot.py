#!/usr/bin/env python3
"""
The frozen Sharadar snapshot: download once, verify, record.

    python3 harness/snapshot.py probe               # key + plan entitlement, no download
    python3 harness/snapshot.py download            # bulk zips -> parquet, needs the key
    python3 harness/snapshot.py verify              # schema, keys, vocabularies, units
    python3 harness/snapshot.py manifest            # write data/SNAPSHOT_MANIFEST.yaml
    python3 harness/snapshot.py status              # what is recorded, DATA_SHA

THE DIRECT SHARADAR API, not Nasdaq Data Link (https://sharadar.com/llms.txt,
copy in data/sharadar_llms.txt). Bulk download is
`GET {api_base}/data/{table}?years=full` with the key in the `x-api-key`
header; the API answers 302 with a pre-signed zip URL, which is fetched WITHOUT
the header. `tickers` only publishes a full snapshot. The key is read from the
environment (`SHARADAR_API_KEY`) or from a gitignored `.env` at the project
root; it is never written anywhere else and never put on a query string.

Why a snapshot and not the API per run: the BQuant project measured its vendor
data moving ~0.03% on composite-level statistics between two fetches of the
same history. Here every run reads the same bytes, verified by sha256 on open,
and the manifest's hash is DATA_SHA on every result. Refreshing the snapshot is
a deliberate re-baseline: `manifest` is in `ask` in .claude/settings.json.
"""

import argparse
import http.client
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.data_layer import REQUIRED_COLUMNS, TICKERS_SCOPE, TICKERS_TABLE_COL, sha256_file  # noqa: E402
from harness.provenance import ROOT, data_sha, load_config, load_runtime  # noqa: E402

# Candidate date columns per table, first present wins. The direct API's bulk
# export names most of them `date`; the legacy export used datekey / filingdate.
DATE_COLS = {"SEP": ["date"], "DAILY": ["date"], "ACTIONS": ["date"], "SF1": ["date", "datekey"],
             "EVENTS": ["date"], "SF2": ["date", "filingdate"], "SF3": ["date", "calendardate"],
             "SP500": ["date"], "METRICS": ["date"]}


def _date_col(table, columns):
    for c in DATE_COLS.get(table, []):
        if c in columns:
            return c
    return None


def _paths(rt):
    root = ROOT / rt["data"]["root"]
    return root, ROOT / rt["data"]["manifest"]


# -----------------------------------------------------------------------------
def load_api_key(rt):
    """Environment first, then the gitignored .env. Never echoed."""
    name = rt["data"]["api_key_env"]
    key = os.environ.get(name)
    if key:
        return key.strip()
    env_file = ROOT / rt["data"].get("env_file", ".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{name}=") :
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"No API key. Set {name} in the environment or in {env_file.name} "
             "(gitignored). Keys come from https://sharadar.com/account.")


def _request(url, key, follow=True, timeout=120):
    req = urllib.request.Request(url, headers={"x-api-key": key, "Accept": "application/json"})
    if follow:
        return urllib.request.urlopen(req, timeout=timeout)

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(_NoRedirect)
    return opener.open(req, timeout=timeout)


def _bulk_location(rt, key, table):
    """Resolve the 302 for a bulk zip WITHOUT downloading it. Returns the
    pre-signed URL, or raises with the API's own error text."""
    api = rt["data"]["api_tables"][table]
    url = f"{rt['data']['api_base']}/data/{api}?years={rt['data']['bulk_history']}"
    try:
        r = _request(url, key, follow=False)
        # 2xx here would be a JSON page, not a bulk file.
        raise RuntimeError(f"{table}: expected a 302 to a zip, got HTTP {r.status}")
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location")
            if not loc:
                raise RuntimeError(f"{table}: redirect without a Location header")
            return loc
        body = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"{table}: HTTP {e.code} — {body}")


def cmd_probe(args):
    """Prove the key works and the plan covers every required table, without
    downloading a byte. 401 = bad key; 403 'Exceeds free tier' = the key is
    not entitled to that table or history."""
    rt = load_runtime()
    key = load_api_key(rt)
    url = f"{rt['data']['api_base']}/data/tickers?ticker=AAPL&format=json"
    try:
        with _request(url, key) as r:
            d = json.loads(r.read().decode())
        print(f"  key OK — tickers?ticker=AAPL returned {d.get('count')} rows")
    except urllib.error.HTTPError as e:
        sys.exit(f"  key REJECTED: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:200]}")
    ok = True
    for t in rt["data"]["required_tables"] + rt["data"]["optional_tables"]:
        try:
            loc = _bulk_location(rt, key, t)
            host = loc.split("/")[2] if "//" in loc else loc[:40]
            print(f"  {t:<8} bulk years={rt['data']['bulk_history']}: 302 -> {host}  OK")
        except RuntimeError as e:
            req = t in rt["data"]["required_tables"]
            print(f"  {t:<8} {'REQUIRED ' if req else 'optional '}NOT AVAILABLE — {e}")
            ok = ok and not req
    print("\n  probe:", "OK — run `snapshot.py download`" if ok else
          "a REQUIRED table is not entitled; fix the plan before downloading")


DATE_LIKE_COLS = ("date", "datekey", "calendardate", "reportperiod", "lastupdated",
             "firstpricedate", "lastpricedate", "firstadded", "filingdate",
             "transactiondate")


def fetch_table(rt, key, table, out, echo=print):
    """Fetch ONE table from the live API and write it to `out` as parquet.

    The bytes that land here came over the wire in this call. Nothing on disk
    is read, trusted or consulted — which is the difference between sourcing
    from the API and validating a cache against it.
    """
    loc = _bulk_location(rt, key, table)
    echo(f"  {table}: downloading bulk zip ...", end="", flush=True)
    with urllib.request.urlopen(urllib.request.Request(loc), timeout=3600) as r:
        blob = r.read()
    echo(f" {len(blob) / 1e6:,.0f} MB")
    zf = zipfile.ZipFile(io.BytesIO(blob))
    members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
    if not members:
        raise RuntimeError(f"{table}: zip holds no CSV ({zf.namelist()[:3]})")
    frames = []
    for m in members:
        with zf.open(m) as fh:
            frames.append(pd.read_csv(fh, low_memory=False))
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    for c in df.columns:
        if c in DATE_LIKE_COLS:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    echo(f"      {len(df):,} rows, {len(df.columns)} columns -> {out.name}")
    return len(df)


def materialise_from_api(dest, tables=None, echo=print):
    """Build a COMPLETE snapshot in `dest` from the live API, plus its manifest.

    This is the `--source api` path: a run that uses it reads no pre-existing
    parquet at all. Returns (dest, manifest_dict). Slow by nature — the bulk
    exports are large — which is the honest cost of constructing from the API
    rather than from a materialisation that was proved equal to it.
    """
    import yaml as _y

    rt = load_runtime()
    key = load_api_key(rt)
    tables = tables or (rt["data"]["required_tables"] + rt["data"]["optional_tables"])
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    entries = {}
    for t in tables:
        out = dest / f"{t}.parquet"
        fetch_table(rt, key, t, out, echo=echo)
        import pyarrow.parquet as pq
        pf = pq.ParquetFile(out)
        entries[t] = {"file": out.name, "rows": pf.metadata.num_rows,
                      "sha256": sha256_file(out), "columns": list(pf.schema.names),
                      "bytes": out.stat().st_size}
    man = {"source": "LIVE Sharadar API fetch at run time (no cached bytes read)",
           "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "api_base": rt["data"]["api_base"], "tables": entries}
    (dest / "MANIFEST.yaml").write_text(_y.safe_dump(man, sort_keys=False))
    return dest, man


def _download_to_file(url, path, refresh_url, attempts=5, chunk=1 << 20):
    """Stream `url` to `path`. On a broken read, re-resolve the pre-signed URL
    (they expire) and resume with a Range request when the server allows it,
    else start over. Returns the byte count."""
    import time as _time
    for attempt in range(1, attempts + 1):
        have = path.stat().st_size if path.exists() else 0
        req = urllib.request.Request(url)
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    if have and r.status != 206:
                        have = 0  # server ignored the range: restart the file
                    mode = "ab" if have else "wb"
                    with open(path, mode) as fh:
                        while True:
                            b = r.read(chunk)
                            if not b:
                                break
                            fh.write(b)
            except urllib.error.HTTPError as e:
                if not (have and e.code == 416):
                    raise
                # 416 on a resume: the part file already holds the whole object.
            # A truncated zip has no central directory and fails to open; the
            # full CRC pass (testzip) over a multi-GB export takes minutes and
            # is not needed to detect truncation.
            with zipfile.ZipFile(path) as z:
                z.namelist()
            return path.stat().st_size
        except (http.client.IncompleteRead, ConnectionError, TimeoutError, OSError,
                zipfile.BadZipFile, urllib.error.URLError) as e:
            print(f"\n      attempt {attempt}/{attempts} failed: {type(e).__name__}: {str(e)[:120]}",
                  flush=True)
            if isinstance(e, zipfile.BadZipFile):
                path.unlink(missing_ok=True)
            _time.sleep(5 * attempt)
            url = refresh_url()
    raise RuntimeError(f"download failed after {attempts} attempts: {path.name}")


def cmd_download(args):
    rt = load_runtime()
    root, _ = _paths(rt)
    key = load_api_key(rt)
    root.mkdir(parents=True, exist_ok=True)
    tables = args.tables or (rt["data"]["required_tables"] + rt["data"]["optional_tables"])
    failed = []
    for t in tables:
        out = root / f"{t}.parquet"
        if out.exists() and not args.force:
            print(f"  {t}: {out.name} exists — skipping (use --force to refetch)")
            continue
        try:
            loc = _bulk_location(rt, key, t)
        except RuntimeError as e:
            print(f"  {t}: {e}")
            failed.append(t)
            continue
        print(f"  {t}: downloading bulk zip ...", end="", flush=True)
        # The pre-signed URL is fetched WITHOUT the api key header. Streamed to
        # a temp file in chunks with retries: a multi-GB read into memory in
        # one call died with IncompleteRead on the first attempt (2026-09-22).
        tmp = out.with_suffix(".zip.part")
        blob_len = _download_to_file(loc, tmp, lambda: _bulk_location(rt, key, t))
        print(f" {blob_len / 1e6:,.0f} MB")
        zf = zipfile.ZipFile(tmp)
        members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        if not members:
            print(f"  {t}: zip holds no CSV ({zf.namelist()[:3]})")
            failed.append(t)
            continue
        frames = []
        for m in members:
            with zf.open(m) as fh:
                frames.append(pd.read_csv(fh, low_memory=False))
        df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
        for c in df.columns:
            if c in ("date", "datekey", "calendardate", "reportperiod", "lastupdated",
                     "firstpricedate", "lastpricedate", "firstadded", "filingdate",
                     "transactiondate"):
                df[c] = pd.to_datetime(df[c], errors="coerce")
        df.to_parquet(out, index=False)
        zf.close()
        tmp.unlink(missing_ok=True)
        print(f"      {len(df):,} rows, {len(df.columns)} columns -> {out.name}")
    if failed:
        print(f"\n  FAILED: {failed}. Required tables must all be present before `verify`.")
        sys.exit(1)
    print("\nNow run:  python3 harness/snapshot.py verify   then   ... manifest")


# -----------------------------------------------------------------------------
def _load(root, t, columns=None):
    p = root / f"{t}.parquet"
    if not p.exists():
        return None
    return pd.read_parquet(p, columns=columns)


def cmd_verify(args):
    """Checks the harness's assumptions against the bytes, and prints the
    vocabularies a human must confirm in config before the first run."""
    rt, cfg = load_runtime(), load_config()
    root, _ = _paths(rt)
    problems, notes = [], []

    for t in rt["data"]["required_tables"]:
        p = root / f"{t}.parquet"
        if not p.exists():
            problems.append(f"{t}: {p} missing")
            continue
        import pyarrow.parquet as pq
        cols = set(pq.ParquetFile(p).schema.names)
        if t == "SF1" and "date" in cols:
            cols.add("datekey")            # the harness's name for SF1.date
        miss = [c for c in REQUIRED_COLUMNS.get(t, []) if c not in cols]
        if miss:
            problems.append(f"{t}: missing required columns {miss}")
    if problems:
        print("\n".join("  !! " + p for p in problems))
        sys.exit(1)

    tk = _load(root, "TICKERS")
    if TICKERS_TABLE_COL in tk.columns:
        notes.append("TICKERS.table values: " + ", ".join(map(str, sorted(tk[TICKERS_TABLE_COL].dropna().unique()))))
        for scope in ("SEP", "SF1"):
            sub = tk[tk[TICKERS_TABLE_COL].isin(TICKERS_SCOPE[scope])].dropna(subset=["ticker", "permaticker"])
            dup = sub.groupby("ticker")["permaticker"].nunique()
            dup = dup[dup > 1]
            if len(dup):
                problems.append(f"TICKERS[{scope}]: {len(dup)} tickers map to >1 permaticker, "
                                f"e.g. {list(dup.index[:5])}")
            notes.append(f"TICKERS[{scope}]: {sub['permaticker'].nunique():,} permatickers")
    notes.append("TICKERS.exchange values: " + ", ".join(map(str, sorted(tk["exchange"].dropna().unique()))))
    notes.append("TICKERS.category values: " + ", ".join(map(str, sorted(tk["category"].dropna().unique()))))
    u = cfg["universe"]
    for k, col in (("exchanges", "exchange"), ("categories", "category")):
        absent = [v for v in u[k] if v not in set(tk[col].dropna().unique())]
        if absent:
            problems.append(f"config universe.{k} names values absent from TICKERS.{col}: {absent}")

    acts = _load(root, "ACTIONS", ["action"])
    vocab = sorted(acts["action"].dropna().unique())
    notes.append("ACTIONS.action vocabulary: " + ", ".join(vocab))
    dl = cfg["returns"]["delisting"]
    for k in ("non_performance_actions", "performance_actions"):
        absent = [a for a in dl.get(k, []) if a not in vocab]
        if absent:
            problems.append(f"config returns.delisting.{k} names actions absent from ACTIONS: "
                            f"{absent}. Fix the config before the first run.")

    import pyarrow.parquet as pq
    _c = pq.ParquetFile(root / "SF1.parquet").schema.names
    _fd = "datekey" if "datekey" in _c else "date"
    notes.append(f"SF1 filing-date column: {_fd}")
    sf1 = _load(root, "SF1", ["dimension", _fd])
    dims = sf1["dimension"].value_counts()
    notes.append("SF1 dimensions: " + ", ".join(f"{d}={n:,}" for d, n in dims.items()))
    if cfg["point_in_time"]["sf1_dimension"] not in dims.index:
        problems.append(f"config point_in_time.sf1_dimension "
                        f"{cfg['point_in_time']['sf1_dimension']} not in SF1")

    for t in rt["data"]["required_tables"] + [x for x in rt["data"]["optional_tables"]
                                              if (root / f"{x}.parquet").exists()]:
        dc = _date_col(t, pq.ParquetFile(root / f"{t}.parquet").schema.names)
        if dc:
            d = _load(root, t, [dc])
            if d is not None and dc in d.columns:
                dd = pd.to_datetime(d[dc])
                notes.append(f"{t}: {len(d):,} rows, {dc} {dd.min().date()} .. {dd.max().date()}")
    # Units: the $100mm screen is written in raw USD. Sharadar documents
    # marketcap in USD, but confirm on the bytes rather than trust it.
    d = _load(root, "DAILY", ["date", "marketcap"])
    last_day = pd.to_datetime(d["date"]).max()
    med = d.loc[pd.to_datetime(d["date"]) == last_day, "marketcap"].median()
    scale = float(cfg["universe"].get("daily_marketcap_scale", 1))
    notes.append(f"DAILY.marketcap median on {last_day.date()}: {med:,.1f} x scale {scale:,.0f} "
                 f"= ${med * scale / 1e6:,.0f}m")
    if not (1e7 <= med * scale <= 1e11):
        problems.append(f"DAILY.marketcap x universe.daily_marketcap_scale gives a median of "
                        f"${med * scale:,.0f}, outside the plausible $10m..$100bn. Fix the scale "
                        "before the first run.")

    sep = _load(root, "SEP", ["date"])
    first = pd.to_datetime(sep["date"]).min()
    from harness.data_layer import build_rebalance_schedule, to_bme
    first_signal = build_rebalance_schedule(cfg["dates"]["eval_start"], cfg["dates"]["eval_end"])[0][1]
    need = to_bme([first_signal - pd.DateOffset(months=12)]).iloc[0]
    notes.append(f"first signal {first_signal.date()}; 12-month momentum needs a price at "
                 f"{need.date()}; SEP starts {first.date()}")
    if first > need:
        problems.append(f"SEP starts {first.date()} but the first signal's 12-month window opens "
                        f"{need.date()}.")
    dd = _load(root, "DAILY", ["date"])
    dfirst = pd.to_datetime(dd["date"]).min()
    if dfirst > first_signal:
        problems.append(f"DAILY starts {dfirst.date()}, after the first signal {first_signal.date()} — "
                        "no market cap for the first universe.")

    print("\n".join("  " + n for n in notes))
    if problems:
        print("\n".join("  !! " + p for p in problems))
        sys.exit(1)
    print("\n  verify: OK. If any vocabulary above disagrees with config/test_config.yaml, "
          "fix the config BEFORE the first run.")


# -----------------------------------------------------------------------------
def cmd_manifest(args):
    rt = load_runtime()
    root, mpath = _paths(rt)
    tables = {}
    for p in sorted(root.glob("*.parquet")):
        t = p.stem
        import pyarrow.parquet as pq
        pf = pq.ParquetFile(p)
        entry = {"file": p.name, "rows": pf.metadata.num_rows, "sha256": sha256_file(p),
                 "columns": list(pf.schema.names), "bytes": p.stat().st_size}
        dc = _date_col(t, entry["columns"])
        if dc:
            d = pd.to_datetime(pd.read_parquet(p, columns=[dc])[dc])
            entry["min_date"] = str(d.min().date())
            entry["max_date"] = str(d.max().date())
        tables[t] = entry
        print(f"  {t:<8} {entry['rows']:>12,} rows  sha256 {entry['sha256'][:12]}")
    if not tables:
        sys.exit(f"no parquet files under {root}")
    m = {
        "schema_version": 1,
        "status": "FROZEN",
        "recorded_on": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Sharadar direct API bulk export (api.sharadar.com/v1.0, years=full), Bundle / Full History",
        "note": ("DATA_SHA is derived from the per-table sha256 values below. "
                 "Re-running `snapshot.py manifest` after a refresh MOVES it and is a "
                 "re-baseline: log it in research/CHANGELOG.md and re-run the baseline."),
        "tables": tables,
    }
    m["data_sha"] = data_sha(m)
    with open(mpath, "w") as f:
        yaml.safe_dump(m, f, sort_keys=False)
    print(f"\n  DATA_SHA {m['data_sha']}  ->  {mpath.relative_to(ROOT)}")


def cmd_status(args):
    rt = load_runtime()
    _, mpath = _paths(rt)
    with open(mpath) as f:
        m = yaml.safe_load(f) or {}
    print(f"  status    {m.get('status')}")
    print(f"  recorded  {m.get('recorded_on')}")
    print(f"  DATA_SHA  {data_sha(m)}")
    for t, e in (m.get("tables") or {}).items():
        print(f"  {t:<8} {e.get('rows', 0):>12,} rows  {e.get('min_date', '?')} .. {e.get('max_date', '?')}")



LIVE_RECORD = ROOT / "research" / "live_check.yaml"


NO_DATE_TABLES = {"TICKERS", "DESCRIPTIONS", "FUNDS"}


def _first_dates(p_file, table):
    """Per-ticker first date, cached — the gate must not re-read SEP every run.

    Keyed by the parquet's size+mtime, so a refreshed table invalidates itself.
    Lives under data/cache, the one place the project may write beneath data/.
    """
    import json as _j

    import pandas as pd
    import pyarrow.parquet as pq

    st = p_file.stat()
    cdir = ROOT / "data" / "cache" / "first_dates"
    cdir.mkdir(parents=True, exist_ok=True)
    cf = cdir / f"{table}.json"
    stamp = f"{st.st_size}:{int(st.st_mtime)}"
    if cf.exists():
        try:
            blob = _j.loads(cf.read_text())
            if blob.get("stamp") == stamp:
                return pd.Series(blob["first"]).astype("datetime64[ns]"), blob["span"]
        except Exception:
            pass
    names = pq.ParquetFile(p_file).schema_arrow.names
    col = next((c for c in ("date", "transactiondate", "calendardate") if c in names), None)
    if col is None or "ticker" not in names:
        return None, None
    df = pd.read_parquet(p_file, columns=["ticker", col])
    df[col] = pd.to_datetime(df[col])
    first = df.groupby("ticker")[col].min().sort_values()
    span = f"{df[col].min().date()}..{df[col].max().date()}"
    cf.write_text(_j.dumps({"stamp": stamp, "span": span,
                            "first": {k: v.strftime("%Y-%m-%d") for k, v in first.items()}}))
    return first, span


def _live_history(rt, key, api_name, p_file, n_sample=6):
    """Does the API publish HISTORY the snapshot does not hold?

    QUERY FORM MATTERS, and getting it wrong makes this check a tautology.
    Measured against the live API 2026-09-22:
      * a bare `to=DATE` (no `ticker`, no `from`) returns 0 rows for EVERY
        date, including dates we know hold data. An earlier version of this
        function used that form, so its "no rows before our start" verdict was
        vacuous - it could never have returned anything else.
      * `sort=date` returns the LATEST row without a ticker filter and the
        EARLIEST row with one. Not stable enough to build on.
      * `ticker=X&from=A&to=B` behaves correctly in both directions and is
        what this function uses.
    Note also that a bogus key is NOT rejected by /data: Sharadar answers 200
    with real rows, so authentication cannot be assumed from a non-empty reply
    either. Hence the positive control below, in the SAME query form.

    Per sampled ticker: ask for rows strictly before the snapshot's first date
    for that ticker (must be none), having first confirmed the same query form
    returns rows just inside its span (the control). Any ticker with earlier
    history at the vendor means our window is shorter than the data allows.
    """
    import json as _j

    import pandas as pd

    first, span = _first_dates(p_file, api_name.upper())
    if first is None:
        return "-", "no date/ticker column"
    # Sample the EARLIEST-listed tickers only. They are the informative ones —
    # if the vendor holds history we lack, it shows up where our record starts
    # earliest. The first version also sampled the NEWEST listings, which broke
    # the control: a ticker whose first row is 2026-06-30 has a control window
    # running past the data edge into the future, so the control legitimately
    # returned nothing and the probe reported itself blind.
    first = first[first < pd.Timestamp("2020-01-01")] if (first < pd.Timestamp("2020-01-01")).any() else first
    sample = list(first.index[:n_sample])
    base = rt["data"]["api_base"]

    def _n(url, tries=2):
        for i in range(tries):
            try:
                with _request(url, key, timeout=180) as r:
                    body = _j.loads(r.read().decode("utf-8", "replace"))
                break
            except Exception:
                if i == tries - 1:
                    raise
        d = body.get("data") if isinstance(body, dict) else body
        return len(d) if isinstance(d, list) else 0

    earlier = []
    for tk in sample:
        lo = first[tk]
        ctl_to = (lo + pd.Timedelta(days=45)).strftime("%Y-%m-%d")
        try:
            if not _n(f"{base}/data/{api_name}?ticker={tk}&from={lo.strftime('%Y-%m-%d')}"
                      f"&to={ctl_to}&limit=1&format=json"):
                return "PROBE FAILED", (f"control returned 0 rows for {tk} inside its own span "
                                        f"({lo.date()}..{ctl_to}) — the probe is blind, so an empty "
                                        "'before' result would prove nothing")
            n_before = _n(f"{base}/data/{api_name}?ticker={tk}&from=1900-01-01"
                          f"&to={(lo - pd.Timedelta(days=1)).strftime('%Y-%m-%d')}&limit=3&format=json")
        except Exception as e:
            return "PROBE FAILED", f"{api_name}/{tk} query raised ({type(e).__name__})"
        if n_before:
            earlier.append(f"{tk}<{lo.date()}")
    if earlier:
        return "MISSING HISTORY", f"{span}; API has earlier rows for {', '.join(earlier)}"
    return "ok", f"{span} ({len(sample)} tickers probed)"


def _write_live_record(rows, problems, absent):
    """Leave the proof on disk so staleness is detectable OFFLINE.

    `records.py check` runs every turn and must not hit the network, but
    "the snapshot is what the vendor publishes" is a claim with a shelf life:
    it is true of the DATA_SHA it was measured against and of no other. So the
    verification writes down which DATA_SHA it checked and when, and the
    offline check refuses a snapshot whose last live verification is missing,
    is against a different DATA_SHA, or has gone stale.
    """
    import datetime
    sys.path.insert(0, str(ROOT / "harness"))
    import provenance

    LIVE_RECORD.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_sha": provenance.data_sha(),
        "api_base": load_runtime()["data"]["api_base"],
        "tables_checked": len(rows),
        "column_complete": not problems,
        "problems": problems,
        "mapped_but_absent": absent,
        "detail": {t: note for t, _a, _n, _sn, note, _h, _hd in rows},
        "history": {t: {"verdict": h, "detail": hd} for t, _a, _n, _sn, _note, h, hd in rows},
        "history_checked": not getattr(_ARGS, "schema_only", False),
    }
    LIVE_RECORD.write_text(yaml.safe_dump(payload, sort_keys=False))


_ARGS = None


def live_report(schema_only=False):
    """Ask the API what it publishes and compare the materialisation to it.

    Returns (rows, problems, absent). `problems` non-empty means the local
    parquet is NOT what Sharadar currently publishes — a missing column, or
    history the API has and we lack. Callable so both `snapshot.py live` and
    `run_test.py` can require the API's authorisation; a run must not measure
    on data the API has not just vouched for.
    """
    import pyarrow.parquet as pq

    rt = load_runtime()
    root, _ = _paths(rt)
    key = load_api_key(rt)
    base = rt["data"]["api_base"]
    problems, rows = [], []
    for t, api_name in rt["data"]["api_tables"].items():
        p_file = root / f"{t}.parquet"
        try:
            with _request(f"{base}/schema/{api_name}?format=postgres", key) as r:
                sql = r.read().decode("utf-8", "replace")
        except Exception as e:
            problems.append(f"{t}: live schema unreadable ({type(e).__name__})")
            continue
        m = re.search(r"CREATE TABLE IF NOT EXISTS \w+ \((.*?)\n\);", sql, re.S)
        api_cols = []
        if m:
            for line in m.group(1).splitlines():
                line = line.strip().rstrip(",")
                if not line or line.upper().startswith(("PRIMARY KEY", "UNIQUE", "CONSTRAINT")):
                    continue
                api_cols.append(line.split()[0].strip('"'))
        if not p_file.exists():
            rows.append((t, api_name, len(api_cols), "-", "ABSENT from snapshot", "-", "not held"))
            continue
        snap_cols = list(pq.ParquetFile(p_file).schema_arrow.names)
        if t == "SF1":
            snap_cols = snap_cols + ["datekey"] if "date" in snap_cols else snap_cols
        missing = [c for c in api_cols if c not in snap_cols]
        note = "ok" if not missing else f"MISSING {', '.join(missing)}"
        if missing:
            problems.append(f"{t}: snapshot lacks columns the API publishes: {missing}")
        if schema_only:
            hist, hist_detail = "skipped", "--schema-only"
        else:
            hist, hist_detail = _live_history(rt, key, api_name, p_file)
            if hist not in ("ok", "-", "skipped"):
                # includes PROBE FAILED: an unreachable table is NOT an
                # authorised one. Silence is not success.
                problems.append(f"{t}: {hist} — {hist_detail}")
        rows.append((t, api_name, len(api_cols), len(snap_cols), note, hist, hist_detail))
    return rows, problems, [r[0] for r in rows if r[4].startswith("ABSENT")]


def cmd_live(args):
    """Prove the frozen snapshot still equals what the API publishes.

    The snapshot exists so every result is reproducible from fixed bytes — but
    "frozen" must mean "a materialisation of the source", not "whatever was
    downloaded once and never checked again". This command is the difference.
    For every table in `api_tables` it compares the live schema's columns, and
    (unless --schema-only) the table's row count and date span, against the
    parquet on disk. A column the API has and the snapshot lacks is a silent
    hole in the candidate pool: it was exactly such a gap, assumed rather than
    measured, that kept four tables out of this snapshot for a whole search.

    Exits non-zero on a real divergence, so it can gate a refresh. `max_date`
    drifting forward is EXPECTED, not a failure: the vendor keeps publishing
    and the snapshot is deliberately pinned behind it.
    """
    global _ARGS
    _ARGS = args
    rows, problems, absent = live_report(schema_only=getattr(args, "schema_only", False))
    print(f"  {'table':<14}{'api':>5}{'snap':>6}  {'columns':<10} {'history':<16} span")
    for t, a, n, sn, note, hist, hd in rows:
        print(f"  {t:<14}{n:>5}{str(sn):>6}  {note[:10]:<10} {hist:<16} {hd}")
    if absent:
        print(f"\n  {len(absent)} mapped table(s) not in the snapshot: {', '.join(absent)}")
        print("  -> `snapshot.py download --tables " + " ".join(absent) + "` then `verify`, `manifest`")
    _write_live_record(rows, problems, absent)
    if problems:
        print("\n" + "\n".join("  !! " + x for x in problems))
        sys.exit(1)
    if getattr(args, "schema_only", False):
        print("\n  columns verified against the live API; HISTORY NOT CHECKED (--schema-only)")
    else:
        print("\n  every mapped table the snapshot holds is column-complete AND carries the API's full history")
    print(f"  recorded in {LIVE_RECORD.relative_to(ROOT)} — `records.py check` DRIFTs when this goes stale")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    d = sub.add_parser("download"); d.add_argument("--tables", nargs="*"); d.add_argument("--force", action="store_true")
    sub.add_parser("verify"); sub.add_parser("manifest"); sub.add_parser("status")
    lv = sub.add_parser("live"); lv.add_argument("--schema-only", action="store_true")
    args = ap.parse_args()
    {"probe": cmd_probe, "download": cmd_download, "verify": cmd_verify,
     "manifest": cmd_manifest, "status": cmd_status, "live": cmd_live}[args.cmd](args)


if __name__ == "__main__":
    main()
