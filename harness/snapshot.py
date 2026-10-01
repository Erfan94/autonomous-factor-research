#!/usr/bin/env python3
"""
The frozen Sharadar snapshot: download once, verify, record.

    python3 harness/snapshot.py probe               # key + plan entitlement, no download
    python3 harness/snapshot.py download            # bulk zips -> parquet, needs the key
    python3 harness/snapshot.py verify              # schema, keys, vocabularies, units
    python3 harness/snapshot.py manifest            # write data/SNAPSHOT_MANIFEST.yaml
    python3 harness/snapshot.py status              # what is recorded, DATA_SHA
    python3 harness/snapshot.py download --tables TB3MS [--fill-latest]   # the external rf table only, keyless

EXTERNAL TABLES (data_layer.EXTERNAL_TABLES; today only FRED TB3MS, the
risk-free series of the excess-hedge diagnostic) sit beside the Sharadar
parquet in the same directory and the same manifest, so DATA_SHA covers them.
They are fetched WITHOUT the Sharadar key from their own public source,
recorded with `kind: external`, `source_url`, `fetched_at` and
`filled_months`, and `live` marks them external rather than asking the
Sharadar API to vouch for bytes it never published. They are deliberately
not in config/runtime.yaml's required/optional_tables: those lists drive
the Sharadar bulk endpoint and the key. A month FRED has not yet published
is filled ONLY with `--fill-latest`, as the mean of the daily DTB3 values
in that month (TB3MS is defined as that average), and the manifest names
every filled month; nothing is forward-filled.

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
from harness.data_layer import (EXTERNAL_COLUMNS, EXTERNAL_TABLES, REQUIRED_COLUMNS,  # noqa: E402
                                TICKERS_SCOPE, TICKERS_TABLE_COL, sha256_file)
from harness.provenance import ROOT, data_sha, load_config, load_runtime  # noqa: E402

# Candidate date columns per table, first present wins. The direct API's bulk
# export names most of them `date`; the legacy export used datekey / filingdate.
DATE_COLS = {"SEP": ["date"], "DAILY": ["date"], "ACTIONS": ["date"], "SF1": ["date", "datekey"],
             "EVENTS": ["date"], "SF2": ["date", "filingdate"], "SF3": ["date", "calendardate"],
             "SP500": ["date"], "METRICS": ["date"]}
DATE_COLS.update({t: ["date"] for t in EXTERNAL_TABLES})


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
    for t in EXTERNAL_TABLES:          # keyless, no fill: what the source publishes now
        out = dest / f"{t}.parquet"
        fetch_external(t, out, echo=echo)
        entries[t] = external_manifest_entry(out, t)
    man = {"source": "LIVE Sharadar API fetch at run time (no cached bytes read)",
           "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "api_base": rt["data"]["api_base"], "tables": entries}
    (dest / "MANIFEST.yaml").write_text(_y.safe_dump(man, sort_keys=False))
    return dest, man


# -----------------------------------------------------------------------------
# External tables (not Sharadar): keyless fetch, frozen beside the Sharadar parquet
# -----------------------------------------------------------------------------
EXTERNAL_META_KEY = b"snapshot_external"
FILL_MIN_DAYS = 10          # a filled month needs at least this many daily observations


def _get_text(url, timeout=120):
    """Plain keyless GET. Deliberately NOT `_request`: no x-api-key header,
    nothing derived from the Sharadar key is ever attached to a third party.
    `file://` URLs work too, which is how the tests stay off the network."""
    with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def parse_fred_csv(text, name="series"):
    """FRED's fredgraph.csv -> DataFrame[date, value]. Read POSITIONALLY: the
    header has been `DATE,<ID>` and is `observation_date,<ID>` today. FRED
    writes a missing value as '.' or an empty field; those parse to NaN."""
    df = pd.read_csv(io.StringIO(text))
    if df.shape[1] < 2 or df.empty:
        raise RuntimeError(f"{name}: not a two-column FRED CSV (header {list(df.columns)[:3]})")
    d = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    if d.isna().any():
        raise RuntimeError(f"{name}: {int(d.isna().sum())} unparseable date(s) in the CSV")
    v = pd.to_numeric(df.iloc[:, 1], errors="coerce").astype(float)
    return pd.DataFrame({"date": d.astype("datetime64[ns]"), "value": v})


def last_completed_month(now=None):
    """The last calendar month that has fully ended, as Period('M')."""
    now = pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz="UTC").tz_localize(None)
    return now.to_period("M") - 1


def daily_month_mean(daily, month, min_days=FILL_MIN_DAYS):
    """(mean, n_days) of the non-missing daily values inside calendar `month`."""
    month = pd.Period(month, "M")
    sub = daily.loc[daily["date"].dt.to_period("M") == month, "value"].dropna()
    if len(sub) < min_days:
        raise RuntimeError(f"fill of {month}: only {len(sub)} daily observation(s) (need {min_days}); "
                           "refusing to fill")
    return float(sub.mean()), int(len(sub))


def build_external(name, fill_through=None, get=_get_text, now=None):
    """(DataFrame[date, value], meta) for one EXTERNAL_TABLES entry, from the
    live source. Monthly: dates must be month starts with no internal gap or
    blank. `fill_through` (a month) appends every month after the source's
    last observation up to it from the daily fill series — only months that
    have ENDED (`now`), each recorded in meta['filled_months']; None fills
    nothing, so a month the source has not published is simply absent."""
    spec = EXTERNAL_TABLES[name]
    df = parse_fred_csv(get(spec["source_url"]), name)
    # trailing blanks are "not yet published"; an internal blank is a hole we refuse
    last_ok = df["value"].last_valid_index()
    if last_ok is None:
        raise RuntimeError(f"{name}: the source holds no values")
    df = df.loc[:last_ok]
    if df["value"].isna().any():
        raise RuntimeError(f"{name}: {int(df['value'].isna().sum())} blank value(s) inside the series")
    if spec.get("frequency") == "monthly" and not (df["date"].dt.day == 1).all():
        raise RuntimeError(f"{name}: monthly series with dates that are not month starts")
    filled, fill_days = {}, {}
    if fill_through is not None:
        target = min(pd.Period(fill_through, "M"), last_completed_month(now))
        last = df["date"].iloc[-1].to_period("M")
        months = list(pd.period_range(last + 1, target, freq="M")) if target > last else []
        if months:
            daily = parse_fred_csv(get(spec["fill_url"]), spec["fill_series"])
            add = []
            for m in months:
                val, n = daily_month_mean(daily, m)
                add.append({"date": m.to_timestamp(), "value": val})
                filled[str(m)] = spec["fill_method"]
                fill_days[str(m)] = n
            df = pd.concat([df, pd.DataFrame(add)], ignore_index=True)
    df = df.reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")
    df["value"] = df["value"].astype(float)
    meta = {"kind": spec["kind"], "source_url": spec["source_url"],
            "fetched_at": (pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz="UTC")
                           ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "units": spec.get("units", ""), "filled_months": filled}
    if filled:
        meta.update({"fill_url": spec["fill_url"], "fill_days": fill_days})
    return df[EXTERNAL_COLUMNS], meta


def write_external(df, meta, out):
    """Parquet with the provenance in the file's own schema metadata, so the
    sha256 (and so DATA_SHA) covers where the bytes came from and which
    months were filled; `manifest` reads it back from the file."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    tbl = pa.Table.from_pandas(df, preserve_index=False)
    md = dict(tbl.schema.metadata or {})
    md[EXTERNAL_META_KEY] = json.dumps(meta, sort_keys=True).encode()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tbl.replace_schema_metadata(md), out)
    return len(df)


def read_external_meta(path):
    import pyarrow.parquet as pq
    md = pq.ParquetFile(path).schema_arrow.metadata or {}
    raw = md.get(EXTERNAL_META_KEY)
    return json.loads(raw.decode()) if raw else {}


def fetch_external(name, out, fill_through=None, echo=print, get=_get_text, now=None):
    df, meta = build_external(name, fill_through=fill_through, get=get, now=now)
    write_external(df, meta, out)
    fs = EXTERNAL_TABLES[name]["fill_series"]
    filled = [f"{m} ({meta['fill_days'][m]} days of {fs})" for m in meta["filled_months"]]
    tail = f"; FILLED {', '.join(filled)}" if filled else ""
    echo(f"  {name}: {len(df):,} rows {df['date'].min().date()} .. {df['date'].max().date()} "
         f"from {meta['source_url']} (keyless){tail} -> {Path(out).name}")
    latest = last_completed_month(now)
    if df["date"].iloc[-1].to_period("M") < latest:
        echo(f"  {name}: !! the source has not published {latest}; the table ends "
             f"{df['date'].iloc[-1].to_period('M')}. Re-run with --fill-latest to fill it from "
             f"{EXTERNAL_TABLES[name]['fill_series']} (recorded in the manifest), or wait.")
    return meta


def verify_external(root, name, cfg=None):
    """(problems, notes) for one external table under `root`. An absent table
    is a note (the excess-hedge diagnostic is then off), not a problem."""
    import pyarrow.parquet as pq
    spec = EXTERNAL_TABLES[name]
    p = Path(root) / f"{name}.parquet"
    problems, notes = [], []
    if not p.exists():
        notes.append(f"{name}: absent (external; the excess-hedge diagnostic is off)")
        return problems, notes
    cols = list(pq.ParquetFile(p).schema_arrow.names)
    if cols != EXTERNAL_COLUMNS:
        problems.append(f"{name}: columns {cols} != {EXTERNAL_COLUMNS}")
        return problems, notes
    df = pd.read_parquet(p)
    d = pd.to_datetime(df["date"])
    v = pd.to_numeric(df["value"], errors="coerce")
    if v.isna().any():
        problems.append(f"{name}: {int(v.isna().sum())} missing value(s)")
    if not (d.dt.day == 1).all():
        problems.append(f"{name}: dates that are not month starts")
    per = d.dt.to_period("M")
    if per.duplicated().any() or not per.is_monotonic_increasing:
        problems.append(f"{name}: months duplicated or out of order")
    elif len(per) and len(per) != (per.iloc[-1] - per.iloc[0]).n + 1:
        problems.append(f"{name}: {(per.iloc[-1] - per.iloc[0]).n + 1 - len(per)} month(s) missing inside "
                        f"{per.iloc[0]}..{per.iloc[-1]}")
    if len(v.dropna()) and not v.dropna().between(-5.0, 30.0).all():
        problems.append(f"{name}: values outside the plausible -5..30 percent range")
    meta = read_external_meta(p)
    if meta.get("source_url") != spec["source_url"] or not meta.get("fetched_at"):
        problems.append(f"{name}: file metadata lacks the source_url / fetched_at it was frozen with")
    filled = meta.get("filled_months") or {}
    for m in filled:
        if pd.Period(m, "M") not in set(per):
            problems.append(f"{name}: filled month {m} is not in the table")
    if cfg is not None and len(per):
        dd = cfg.get("dates", {})
        need_lo = pd.Period(pd.Timestamp(dd["eval_start"]), "M")
        need_hi = pd.Period(pd.Timestamp(dd["eval_end"]), "M")
        if per.iloc[0] > need_lo or per.iloc[-1] < need_hi:
            problems.append(f"{name}: {per.iloc[0]}..{per.iloc[-1]} does not cover the decision window "
                            f"{need_lo}..{need_hi}")
        oos_end = str(dd.get("out_of_sample_end", ""))
        if oos_end and oos_end.lower() != "rolling" and per.iloc[-1] < pd.Period(pd.Timestamp(oos_end), "M"):
            notes.append(f"{name}: ends {per.iloc[-1]}, before the holdout end {oos_end[:7]} — the excess "
                         "diagnostic will drop those months (fill with `download --tables "
                         f"{name} --force --fill-latest` once the month has closed)")
    notes.append(f"{name}: {len(df):,} rows, {per.iloc[0] if len(per) else '?'} .. "
                 f"{per.iloc[-1] if len(per) else '?'} (external, {spec['source_url']}; fetched "
                 f"{meta.get('fetched_at', '?')}; filled {filled or 'none'})")
    return problems, notes


def external_manifest_entry(p, name):
    """The manifest row of an external table: the Sharadar row's fields, plus
    kind / source_url / fetched_at / filled_months read from the file itself."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(p)
    meta = read_external_meta(p)
    d = pd.to_datetime(pd.read_parquet(p, columns=["date"])["date"])
    entry = {"file": Path(p).name, "rows": pf.metadata.num_rows, "sha256": sha256_file(p),
             "columns": list(pf.schema.names), "bytes": Path(p).stat().st_size,
             "min_date": str(d.min().date()), "max_date": str(d.max().date()),
             "kind": "external", "source_url": meta.get("source_url", EXTERNAL_TABLES[name]["source_url"]),
             "fetched_at": meta.get("fetched_at"), "filled_months": dict(meta.get("filled_months") or {})}
    if meta.get("filled_months"):
        entry["fill_url"] = meta.get("fill_url")
        entry["fill_days"] = dict(meta.get("fill_days") or {})
    return entry


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
    root.mkdir(parents=True, exist_ok=True)
    tables = args.tables or (rt["data"]["required_tables"] + rt["data"]["optional_tables"]
                             + list(EXTERNAL_TABLES))
    external = [t for t in tables if t in EXTERNAL_TABLES]
    tables = [t for t in tables if t not in EXTERNAL_TABLES]
    # The Sharadar key is loaded only when a Sharadar table is being fetched,
    # so `--tables TB3MS` runs keyless.
    key = load_api_key(rt) if tables else None
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
    fill_through = last_completed_month() if getattr(args, "fill_latest", False) else None
    for t in external:
        out = root / f"{t}.parquet"
        if out.exists() and not args.force:
            print(f"  {t}: {out.name} exists — skipping (use --force to refetch)")
            continue
        try:
            fetch_external(t, out, fill_through=fill_through)
        except Exception as e:
            print(f"  {t}: external fetch FAILED — {type(e).__name__}: {e}")
            failed.append(t)
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

    for t in EXTERNAL_TABLES:
        xp, xn = verify_external(root, t, cfg)
        problems += xp
        notes += xn
    print("\n".join("  " + n for n in notes))
    if problems:
        print("\n".join("  !! " + p for p in problems))
        sys.exit(1)
    print("\n  verify: OK. If any vocabulary above disagrees with config/test_config.yaml, "
          "fix the config BEFORE the first run.")


# -----------------------------------------------------------------------------
def build_manifest(root, echo=print):
    """The manifest dict for every parquet under `root` (pure of paths: the
    caller decides where it is written). External tables get their extra
    provenance fields (external_manifest_entry); Sharadar rows are unchanged."""
    import pyarrow.parquet as pq
    root = Path(root)
    tables = {}
    for p in sorted(root.glob("*.parquet")):
        t = p.stem
        if t in EXTERNAL_TABLES:
            entry = external_manifest_entry(p, t)
        else:
            pf = pq.ParquetFile(p)
            entry = {"file": p.name, "rows": pf.metadata.num_rows, "sha256": sha256_file(p),
                     "columns": list(pf.schema.names), "bytes": p.stat().st_size}
            dc = _date_col(t, entry["columns"])
            if dc:
                d = pd.to_datetime(pd.read_parquet(p, columns=[dc])[dc])
                entry["min_date"] = str(d.min().date())
                entry["max_date"] = str(d.max().date())
        tables[t] = entry
        echo(f"  {t:<8} {entry['rows']:>12,} rows  sha256 {entry['sha256'][:12]}"
             + ("  (external)" if entry.get("kind") == "external" else ""))
    if not tables:
        return None
    ext = [t for t, e in tables.items() if e.get("kind") == "external"]
    source = "Sharadar direct API bulk export (api.sharadar.com/v1.0, years=full), Bundle / Full History"
    if ext:
        source += "; external (kind: external, keyless public source): " + ", ".join(ext)
    m = {
        "schema_version": 1,
        "status": "FROZEN",
        "recorded_on": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "note": ("DATA_SHA is derived from the per-table sha256 values below. "
                 "Re-running `snapshot.py manifest` after a refresh MOVES it and is a "
                 "re-baseline: log it in research/CHANGELOG.md and re-run the baseline."),
        "tables": tables,
    }
    m["data_sha"] = data_sha(m)
    return m


def cmd_manifest(args):
    rt = load_runtime()
    root, mpath = _paths(rt)
    m = build_manifest(root)
    if m is None:
        sys.exit(f"no parquet files under {root}")
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
        tag = ""
        if e.get("kind") == "external":
            tag = (f"  external ({e.get('source_url')}; fetched {e.get('fetched_at')}; filled "
                   f"{e.get('filled_months') or 'none'})")
        print(f"  {t:<8} {e.get('rows', 0):>12,} rows  {e.get('min_date', '?')} .. {e.get('max_date', '?')}{tag}")



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


def external_report(root=None):
    """What `live` says about each external table the snapshot holds: that it
    is external, where it came from, and that the Sharadar API did NOT vouch
    for it (it cannot: it never published it). No network call."""
    if root is None:
        root, _ = _paths(load_runtime())
    out = {}
    for t, spec in EXTERNAL_TABLES.items():
        p = Path(root) / f"{t}.parquet"
        if not p.exists():
            continue
        meta = read_external_meta(p)
        out[t] = {"kind": "external", "vouched_by_api": False,
                  "source_url": meta.get("source_url", spec["source_url"]),
                  "fetched_at": meta.get("fetched_at"),
                  "filled_months": dict(meta.get("filled_months") or {})}
    return out


def _write_live_record(rows, problems, absent, external=None):
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
        "sharadar_tables_held": len(rows) - len(absent),
        "column_complete": not problems,
        "problems": problems,
        "mapped_but_absent": absent,
        "detail": {t: note for t, _a, _n, _sn, note, _h, _hd in rows},
        "history": {t: {"verdict": h, "detail": hd} for t, _a, _n, _sn, _note, h, hd in rows},
        "history_checked": not getattr(_ARGS, "schema_only", False),
        "external_tables": external or {},
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
    external = external_report()
    for t, e in external.items():
        print(f"  {t:<14}{'-':>5}{'-':>6}  {'external':<10} {'not vouched':<16} {e['source_url']} "
              f"(fetched {e['fetched_at']}; filled {e['filled_months'] or 'none'})")
    _write_live_record(rows, problems, absent, external)
    if problems:
        print("\n" + "\n".join("  !! " + x for x in problems))
        sys.exit(1)
    if getattr(args, "schema_only", False):
        print("\n  columns verified against the live API; HISTORY NOT CHECKED (--schema-only)")
    else:
        print("\n  every mapped table the snapshot holds is column-complete AND carries the API's full history")
    if external:
        print(f"  external table(s) {', '.join(external)}: NOT Sharadar's, so not vouched for by its API "
              "(sha256 still checked on every open)")
    print(f"  recorded in {LIVE_RECORD.relative_to(ROOT)} — `records.py check` DRIFTs when this goes stale")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    d = sub.add_parser("download"); d.add_argument("--tables", nargs="*"); d.add_argument("--force", action="store_true")
    d.add_argument("--fill-latest", action="store_true",
                   help="external tables: fill months the source has not yet published, up to the last "
                        "completed month, from the daily fill series (recorded in the manifest)")
    sub.add_parser("verify"); sub.add_parser("manifest"); sub.add_parser("status")
    lv = sub.add_parser("live"); lv.add_argument("--schema-only", action="store_true")
    args = ap.parse_args()
    {"probe": cmd_probe, "download": cmd_download, "verify": cmd_verify,
     "manifest": cmd_manifest, "status": cmd_status, "live": cmd_live}[args.cmd](args)


if __name__ == "__main__":
    main()
