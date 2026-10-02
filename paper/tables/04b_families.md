*Table 04b_families. The nine families. Source: research/families.yaml `families`; the v14 column from MODEL_MANIFEST.yaml v14 `families`.*

| family | definition | members | members (seeds first, passers in assignment order) | in v14 |
|---|---|---|---|---|
| size | market capitalisation (small = attractive) | 1 | Size | Size |
| value | price relative to a fundamental anchor | 4 | Value, CF, NetPayoutYield, cfp | Value, cfp |
| profitability | earning power relative to capital | 6 | Profitability, CBOperProf, GP, OperProfRD, RoE, roaq | Profitability, CBOperProf, GP, roaq, RoE |
| investment | growth of the asset base or of investment | 2 | Investment, PctAcc | Investment, PctAcc |
| momentum | continuation of past returns | 2 | Momentum, TrendFactor | Momentum, TrendFactor |
| volatility | dispersion or tail size of a stock's own returns (total, idiosyncratic, extreme daily); low = attractive | 4 | IdioVol3F, IdioVolAHT, MaxRet, RealizedVol | MaxRet, IdioVol3F |
| external_financing | net capital raised from or returned to investors (share issuance, net equity and debt financing) | 4 | NetEquityFinance, ShareIss1Y, ShareIss5Y, XFIN | ShareIss5Y, XFIN |
| short_term_reversal | reversal of the most recent month's return | 1 | STreversal | STreversal |
| liquidity | trading activity and trading cost (turnover, zero-volume days, bid-ask spread, volume trend) | 5 | VolumeTrend, zerotrade12M, zerotrade1M, zerotrade6M, BidAskSpreadFlip | zerotrade6M, VolumeTrend |
