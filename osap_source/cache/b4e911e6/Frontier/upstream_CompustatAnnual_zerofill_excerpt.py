# Fall back to dcvt for remaining missing convertible debt values
mask_dc3 = compustat_data['dc'].isna()
compustat_data.loc[mask_dc3, 'dc'] = compustat_data.loc[mask_dc3, 'dcvt']

# Create zero-filled versions of expense variables
compustat_data['xint0'] = 0.0  # 0.0 ensures float64
compustat_data.loc[compustat_data['xint'].notna(), 'xint0'] = compustat_data['xint']

compustat_data['xsga0'] = 0.0
compustat_data.loc[compustat_data['xsga'].notna(), 'xsga0'] = compustat_data['xsga']

compustat_data['xad0'] = compustat_data['xad'].fillna(0)

# Fill missing values with zero for specified balance sheet and income statement items
zero_fill_vars = ['nopi', 'dvt', 'ob', 'dm', 'dc', 'aco', 'ap', 'intan', 'ao',
                  'lco', 'lo', 'rect', 'invt', 'drc', 'spi', 'gdwl', 'che',
                  'dp', 'act', 'lct', 'tstkp', 'dvpa', 'scstkc', 'sstk',
                  'mib', 'ivao', 'prstkc', 'prstkcc', 'txditc', 'ivst']

for var in zero_fill_vars:
    compustat_data[var] = compustat_data[var].fillna(0)

# Download CCM linking table data directly (removing dependency on CCMLinkingTable.py)
print("Downloading CCM linking table data...", flush=True)
CCM_QUERY = """
SELECT a.gvkey, a.conm, a.tic, a.cusip, a.cik, a.sic, a.naics,
# Create annual version of the dataset
annual_data = compustat_data.copy()

# Remove CCM linking metadata columns
annual_data = annual_data.drop(columns=['timeLinkStart_d', 'timeLinkEnd_d', 'linkprim', 'liid', 'linktype'])

# Convert gvkey to numeric format
annual_data['gvkey'] = pd.to_numeric(annual_data['gvkey'])

# Add 6-month reporting lag to determine data availability date
annual_data['time_avail_m'] = (
    annual_data['datadate'].dt.to_period('M') + 6
).dt.to_timestamp()

# Save annual version
annual_data.to_parquet("../pyData/Intermediate/a_aCompustat.parquet", index=False)
print(f"Annual version saved with {len(annual_data)} records", flush=True)

# Create monthly version by expanding annual data
monthly_data = annual_data.copy()

# Replicate each annual record 12 times for monthly availability
monthly_data = pd.concat([monthly_data] * 12, ignore_index=True)

# Add sequential month offsets within each gvkey-time group
monthly_data = monthly_data.sort_values(['gvkey', 'time_avail_m']).reset_index(drop=True)
monthly_data['tempTime'] = monthly_data['time_avail_m']
monthly_data['month_offset'] = monthly_data.groupby(['gvkey', 'tempTime']).cumcount()

# Apply month offsets to create monthly availability dates
monthly_data['time_avail_m'] = (
    monthly_data['time_avail_m'].dt.to_period('M') + monthly_data['month_offset']
).dt.to_timestamp()

monthly_data = monthly_data.drop('tempTime', axis=1)

# Remove duplicates keeping most recent data for each gvkey-month and permno-month
monthly_data = monthly_data.sort_values(['gvkey', 'time_avail_m', 'datadate'])
monthly_data = monthly_data.drop_duplicates(['gvkey', 'time_avail_m'], keep='last')

monthly_data = monthly_data.sort_values(['permno', 'time_avail_m', 'datadate'])
monthly_data = monthly_data.drop_duplicates(['permno', 'time_avail_m'], keep='last')

monthly_data = monthly_data.drop(columns=['month_offset'])

# Save monthly version
monthly_data.to_parquet("../pyData/Intermediate/m_aCompustat.parquet", index=False)
print(f"Monthly version saved with {len(monthly_data)} records", flush=True)
