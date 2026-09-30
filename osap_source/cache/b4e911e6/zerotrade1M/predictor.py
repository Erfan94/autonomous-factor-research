# Shared source with zerotrade6M/zerotrade12M — see osap_source/cache/b4e911e6/zerotrade6M/predictor.py
# for the full fetched script (ZZ1_zerotrade_zerotradeAlt1_zerotradeAlt12.py at ref b4e911e69678a7424f318617a61d813f54183123).
# zerotrade1M-specific lines only, reproduced here for this cache entry:
#
# df["countzero"] = np.where(df["vol"] == 0, 1, 0)
# df["turn"] = df["vol"] / df["shrout"]
# collapsed = df.groupby(["permno","time_avail_m"]).agg({"countzero":"sum","turn":"sum","days":"count"}).reset_index()
# collapsed = collapsed.rename(columns={"days": "ndays"})
# collapsed["temp_zerotrade"] = (collapsed["countzero"] + ((1 / collapsed["turn"]) / 480000)) * (21 / collapsed["ndays"])
# collapsed["zerotrade1M"] = grouped["temp_zerotrade"].shift(1)
