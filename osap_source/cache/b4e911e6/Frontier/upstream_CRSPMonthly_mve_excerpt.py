crsp_data.loc[mask3, 'ret'] = crsp_data.loc[mask3, 'dlret']

# Convert units and compute market value of equity
crsp_data['shrout'] = crsp_data['shrout'] / 1000
crsp_data['vol'] = crsp_data['vol'] / 10000
crsp_data['mve_c'] = crsp_data['shrout'] * np.abs(crsp_data['prc'])

# Aggregate to permco level to obtain company-level market equity
mve_permco = (
    crsp_data.dropna(subset=['permco'])
    .groupby(['permco', 'time_avail_m'], as_index=False)['mve_c']
    .sum(min_count=1)
    .rename(columns={'mve_c': 'mve_permco'})
)
crsp_data = crsp_data.merge(mve_permco, on=['permco', 'time_avail_m'], how='left')

# Clean up unnecessary columns
