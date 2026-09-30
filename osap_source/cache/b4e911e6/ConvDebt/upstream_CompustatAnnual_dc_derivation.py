# Excerpt from Signals/pyCode/DataDownloads/CompustatAnnual.py (ref b4e911e6)
# SQL SELECT (line 41) includes: a.csho,a.cshrc,a.dcpstk,a.dcvt,a.dlc,a.dlcch,a.dltis,a.dltr,...
# Lines 106-127 verbatim (derivation of the 'dc' column consumed by Predictors/ConvDebt.py):

# Create derived variable: convertible debt (dc) using complex logic
compustat_data['dc'] = np.nan
# Calculate convertible debt as difference when dcpstk > pstk and dcvt is missing
mask_dc1 = (
    (compustat_data['dcpstk'] > compustat_data['pstk']) &
    compustat_data['pstk'].notna() &
    compustat_data['dcpstk'].notna() &
    compustat_data['dcvt'].isna()
)
compustat_data.loc[mask_dc1, 'dc'] = (
    compustat_data.loc[mask_dc1, 'dcpstk'] - compustat_data.loc[mask_dc1, 'pstk']
)
# Use dcpstk directly when pstk is missing and dcvt is missing
mask_dc2 = (
    compustat_data['pstk'].isna() &
    compustat_data['dcpstk'].notna() &
    compustat_data['dcvt'].isna()
)
compustat_data.loc[mask_dc2, 'dc'] = compustat_data.loc[mask_dc2, 'dcpstk']
# Fall back to dcvt for remaining missing convertible debt values
mask_dc3 = compustat_data['dc'].isna()
compustat_data.loc[mask_dc3, 'dc'] = compustat_data.loc[mask_dc3, 'dcvt']
