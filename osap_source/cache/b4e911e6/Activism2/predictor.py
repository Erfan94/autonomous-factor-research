# Source: Signals/pyCode/Predictors/ZZ1_Activism1_Activism2.py
# Fetched from https://raw.githubusercontent.com/OpenSourceAP/CrossSection/b4e911e69678a7424f318617a61d813f54183123/Signals/pyCode/Predictors/ZZ1_Activism1_Activism2.py
# NOTE: this script emits BOTH Activism1 and Activism2 (Cremers and Nair 2005, Tables 3A/4A).
# Cached verbatim for provenance; Activism2's own construction is described in spec.md.

# ABOUTME: Activism1 (takeover vulnerability) and Activism2 (active shareholders) following Cremers and Nair 2005, Tables 3A and 4A
# ABOUTME: Creates shareholder activism proxy predictors based on institutional ownership and governance metrics

"""
ZZ1_Activism1_Activism2.py

How to run:
    python3 Predictors/ZZ1_Activism1_Activism2.py

Inputs:
    - ../pyData/Intermediate/SignalMasterTable.parquet
    - ../pyData/Intermediate/TR_13F.parquet (for maxinstown_perc)
    - ../pyData/Intermediate/monthlyCRSP.parquet (for shrcls)
    - ../pyData/Intermediate/GovIndex.parquet (for G variable)

Outputs:
    - ../pyData/Predictors/Activism1.csv (permno, yyyymm, Activism1)
    - ../pyData/Predictors/Activism2.csv (permno, yyyymm, Activism2)

Signal Construction:
    - Activism1: Shareholder activism proxy 1: External Gov among Large Blockheld
    - Activism2: Shareholder activism proxy 2: Blockholdings among High External Governance
"""

import pandas as pd
import polars as pl
import numpy as np
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.save_standardized import save_predictor
from utils.stata_fastxtile import fastxtile

# DATA LOAD
print("Loading SignalMasterTable...")
df = pl.read_parquet("../pyData/Intermediate/SignalMasterTable.parquet").select(
    ["permno", "time_avail_m", "ticker", "exchcd"]
)

print(f"Initial data loaded: {df.shape[0]} rows")

print("Merging with TR_13F...")
tr13f = pl.read_parquet("../pyData/Intermediate/TR_13F.parquet").select(
    ["permno", "time_avail_m", "maxinstown_perc"]
)

df = df.join(tr13f, on=["permno", "time_avail_m"], how="left")
print(f"After TR_13F merge: {df.shape[0]} rows")

print("Merging with monthlyCRSP...")
mcrsp = pl.read_parquet("../pyData/Intermediate/monthlyCRSP.parquet").select(
    ["permno", "time_avail_m", "shrcls"]
)

df = df.join(mcrsp, on=["permno", "time_avail_m"], how="left")
print(f"After monthlyCRSP merge: {df.shape[0]} rows")

print("Handling ticker-based merge with GovIndex...")
temp_missing_ticker = df.filter(pl.col("ticker").is_null())
df = df.filter(pl.col("ticker").is_not_null())

print(f"Records with ticker: {df.shape[0]}")
print(f"Records without ticker: {temp_missing_ticker.shape[0]}")

gov = pl.read_parquet("../pyData/Intermediate/GovIndex.parquet")
df = df.join(gov, on=["ticker", "time_avail_m"], how="left")

gov_columns = [col for col in df.columns if col not in temp_missing_ticker.columns]
for col in gov_columns:
    temp_missing_ticker = temp_missing_ticker.with_columns(pl.lit(None).alias(col))

df = pl.concat([df, temp_missing_ticker])
print(f"After GovIndex merge and append: {df.shape[0]} rows")

# SIGNAL CONSTRUCTION

# Activism1 (not this acronym's target signal; kept because the script emits both)
print("Constructing Activism1 signal...")
tempBLOCK = (
    pl.when(pl.col("maxinstown_perc") > 5).then(pl.col("maxinstown_perc")).otherwise(0)
)
df = df.with_columns(tempBLOCK.alias("tempBLOCK"))

with np.errstate(over="ignore", invalid="ignore"):
    df_pandas = df.to_pandas()
    df_pandas["tempBLOCKQuant"] = fastxtile(
        df_pandas, "tempBLOCK", by="time_avail_m", n=4
    )
    df = pl.from_pandas(df_pandas)

df = df.with_columns(
    pl.when(pl.col("G").is_null())
    .then(None)
    .otherwise(24 - pl.col("G"))
    .alias("tempEXT")
)

df = df.with_columns(
    pl.when(pl.col("tempBLOCKQuant") <= 3)
    .then(None)
    .when(pl.col("shrcls") != "")
    .then(None)
    .otherwise(pl.col("tempEXT"))
    .alias("tempEXT")
)

df = df.with_columns(pl.col("tempEXT").alias("Activism1"))
df = df.drop(["tempBLOCK", "tempBLOCKQuant", "tempEXT"])

# Activism2: THIS acronym
print("Constructing Activism2 signal...")
tempBLOCK = (
    pl.when(pl.col("maxinstown_perc") > 5).then(pl.col("maxinstown_perc")).otherwise(0)
)
df = df.with_columns(tempBLOCK.alias("tempBLOCK"))

# Exclude firms with missing governance data and dual-class shares
df = df.with_columns(
    pl.when(pl.col("G").is_null())
    .then(None)
    .when((pl.col("shrcls") != "") & (pl.col("shrcls").is_not_null()))
    .then(None)  # Exclude dual class shares
    .otherwise(pl.col("tempBLOCK"))
    .alias("tempBLOCK")
)

# Restrict to firms with high external governance (external governance >= 19, i.e. G <= 5)
df = df.with_columns(
    pl.when((24 - pl.col("G")) < 19)
    .then(None)
    .otherwise(pl.col("tempBLOCK"))
    .alias("tempBLOCK")
)

df = df.with_columns(pl.col("tempBLOCK").alias("Activism2"))

# SAVE
save_predictor(df.to_pandas(), "Activism1")
save_predictor(df.to_pandas(), "Activism2")
