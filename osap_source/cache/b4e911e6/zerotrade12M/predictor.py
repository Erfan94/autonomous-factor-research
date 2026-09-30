# Shared source with zerotrade1M/zerotrade6M — see osap_source/cache/b4e911e6/zerotrade6M/predictor.py
# for the full fetched script (ZZ1_zerotrade_zerotradeAlt1_zerotradeAlt12.py at ref b4e911e69678a7424f318617a61d813f54183123).
# zerotrade12M-specific lines only, reproduced here for this cache entry:
#
# collapsed["Turn12"] = turn + shift(1..11) summed (12 calendar months, current + 11 lags)
# collapsed["countzero12"] = countzero + shift(1..11) summed
# collapsed["ndays12"] = ndays + shift(1..11) summed
# collapsed["temp_zerotrade12"] = (collapsed["countzero12"] + ((1 / collapsed["Turn12"]) / 11000)) * (21 * 12 / collapsed["ndays12"])
# collapsed["zerotrade12M"] = grouped["temp_zerotrade12"].shift(1)
