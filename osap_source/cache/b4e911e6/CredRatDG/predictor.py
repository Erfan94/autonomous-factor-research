# ABOUTME: Credit Rating Downgrade following Dichev and Piotroski 2001, Table 4, Downgrade BHAR 3-month
# ABOUTME: calculates credit rating downgrade signal - 1 if downgrade in past 6 months

"""
CredRatDG.py

Usage:
    Run from [Repo-Root]/Signals/pyCode/
    python3 Predictors/CredRatDG.py

Inputs:
    - m_SP_creditratings.parquet: S&P credit ratings data with columns [gvkey, time_avail_m, credrat]
    - m_CIQ_creditratings.parquet: CIQ credit ratings data with columns [gvkey, ratingdate, source, anydowngrade]
    - SignalMasterTable.parquet: Monthly master table with columns [gvkey, permno, time_avail_m]

Outputs:
    - CredRatDG.csv: CSV file with columns [permno, yyyymm, CredRatDG]
    - CredRatDG = 1 if credit rating downgrade occurred in past 6 months, else 0
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.save_standardized import save_predictor

print("Starting CredRatDG predictor...")

print("Loading m_SP_creditratings data...")
comp_df = pd.read_parquet(
    "../pyData/Intermediate/m_SP_creditratings.parquet",
    columns=["gvkey", "time_avail_m", "credrat"],
)

comp_df["gvkey"] = comp_df["gvkey"].astype(np.int64)
comp_df["time_avail_m"] = comp_df["time_avail_m"].dt.to_period("M")

comp_df = comp_df.sort_values(["gvkey", "time_avail_m"])
comp_df["l_credrat"] = comp_df.groupby("gvkey")["credrat"].shift(1)
comp_df["downgrade_sp"] = np.where(
    comp_df["credrat"] - comp_df["l_credrat"] < 0, 1, np.nan
)

comp_df.query("downgrade_sp == 1", inplace=True)
comp_df = comp_df[["gvkey", "time_avail_m", "downgrade_sp"]]

print(f"Generated dataset of {comp_df['downgrade_sp'].notna().sum():,} SP downgrades")

print("Loading m_CIQ_creditratings data...")
ciq_df = pd.read_parquet(
    "../pyData/Intermediate/m_CIQ_creditratings.parquet",
    columns=["gvkey", "ratingdate", "source", "anydowngrade"],
)
ciq_df["gvkey"] = ciq_df["gvkey"].astype(np.int64)
ciq_df["ratingdate"] = pd.to_datetime(ciq_df["ratingdate"]).dt.to_period("M")
ciq_df.rename(
    columns={"ratingdate": "time_avail_m", "anydowngrade": "downgrade_ciq"},
    inplace=True,
)

ciq_df.query("downgrade_ciq == 1", inplace=True)

ciq_df = (
    ciq_df.groupby(["gvkey", "time_avail_m"])
    .agg({"downgrade_ciq": "max"})
    .reset_index()
)

print("Loading SignalMasterTable...")
signal_master = pd.read_parquet(
    "../pyData/Intermediate/SignalMasterTable.parquet",
    columns=["gvkey", "permno", "time_avail_m"],
).dropna(subset=["gvkey"])

signal_master["gvkey"] = signal_master["gvkey"].astype(np.int64)
signal_master["time_avail_m"] = signal_master["time_avail_m"].dt.to_period("M")

print(f"Loaded {len(signal_master):,} SignalMasterTable observations")

print("Merging data...")
df = pd.merge(signal_master, comp_df, on=["gvkey", "time_avail_m"], how="left")
df = pd.merge(df, ciq_df, on=["gvkey", "time_avail_m"], how="left")

df["dg_cur"] = df["downgrade_sp"].fillna(df["downgrade_ciq"])
df["dg_cur"] = df["dg_cur"].fillna(0)

print(f"After merging: {len(df):,} observations")

print("Constructing CredRatDG signal...")

df.sort_values(["permno", "time_avail_m"], inplace=True)
df.set_index(["permno", "time_avail_m"], inplace=True)
df["CredRatDG"] = (
    df.groupby("permno")["dg_cur"]
    .rolling(6, min_periods=1)
    .max()
    .reset_index(level=0, drop=True)
)
df.reset_index(inplace=True)

print("Saving predictor...")

df["time_avail_m"] = df["time_avail_m"].dt.to_timestamp()

save_predictor(df, "CredRatDG")

print("CredRatDG predictor completed successfully!")
