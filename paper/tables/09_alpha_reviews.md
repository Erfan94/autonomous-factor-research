*Table 09_alpha_reviews. Every alpha-reviewer audit. Source: events `alpha_review` (finding lists counted).*

| events line | ts | target | findings by severity | verdict |
|---|---|---|---|---|
| 67 | 2026-09-30T17:16:42Z | batch01: AM, Accruals | critical 0, major 0, minor 5 |  |
| 97 | 2026-09-30T17:34:33Z | batch02: AnnouncementReturn, BMdec, BPEBM, Beta, BetaFP | critical 0, major 2, minor 5 |  |
| 151 | 2026-09-30T17:57:42Z | batch03: BetaLiquidityPS, BetaTailRisk, BidAskSpread, BookLeverage, CBOperProf, CF | critical 0, major 0, minor 3 |  |
| 164 | 2026-09-30T18:05:10Z | batch04: Cash, CashProd, ChAssetTurnover, ChEQ, ChInv, ChInvIA | critical 0, major 0, minor 5 |  |
| 224 | 2026-09-30T18:40:00Z | batch05-06: ChNNCOA, ChNWC, ChTax, CompEquIss, CompositeDebtIssuance, CoskewACX, Coskewness, DelCOA | critical 0, major 1, minor 4 |  |
| 234 | 2026-09-30T18:55:00Z | batch07: DelCOL, DelEqu, DelFINL, DelNetFin | critical 0, major 1, medium 1, minor 4 |  |
| 274 | 2026-09-30T20:45:00Z | batch08: DolVol, EBM, EP, EarningsConsistency | critical 0, major 0, medium 1, minor 4 |  |
| 293 | 2026-09-30T21:35:00Z | batch09: EquityDuration, EarningsSurprise, EntMult | critical 0, high 0, medium 2, low 8 |  |
| 321 | 2026-09-30T23:10:00Z | fetch10-11: GP, GrLTNOA, GrSaleToGrInv, GrSaleToGrOverhead, Herf, HerfAsset, HerfBE, High52 | critical 0, high 0, medium 1, low 6 |  |
| 359 | 2026-10-01T01:20:00Z | batch12: IdioVol3F, IdioVolAHT, Illiquidity, IntMom, IntanBM | critical 0, major 1, minor 5 |  |
| 387 | 2026-10-01T02:55:00Z | batch13: InvestmentTWX, LRreversal, Leverage, InvGrowth, IntanSP, IntanEP, IntanCFP | critical 0, major 0, minor 4 |  |
| 410 | 2026-10-01T04:25:00Z | batch14: Mom6m, Mom12mOffSeason, MomOffSeason, MRreversal, MaxRet, MeanRankRevGrowth | critical 0, major 1, minor 4 |  |
| 447 | 2026-09-30T21:19:00Z | batch15-16: MomOffSeason06YrPlus, MomSeason, MomSeason06YrPlus, MomSeasonShort, NOA, NetDebtFinance, NetEquityFinance, N … | critical 0, high 0, medium 1, low 5 |  |
| 484 | 2026-09-30T21:43:50Z | batch17: OPLeverage, OperProfRD, OrgCap | critical 0, major 2, minor 5 |  |
| 496 | 2026-09-30T21:54:22Z | batch18: PctAcc, PctTotAcc, Price, PriceDelayRsq | critical 1, major 0, minor 3 |  |
| 516 | 2026-09-30T22:05:06Z | batch19: PriceDelaySlope, PriceDelayTstat | critical 0, major 0, minor 3 |  |
| 572 | 2026-09-30T22:34:37Z | batch20-21: RealizedVol, RoE, SP, STreversal, ShareIss1Y | critical 0, major 0, medium 1, minor 5 |  |
| 633 | 2026-09-30T22:56:02Z | batch21-23: ResidualMomentum, ReturnSkew, ReturnSkew3F, RevenueSurprise, ShareIss5Y, VolMkt, VolSD, VolumeTrend, XFIN | critical 0, major 2, minor 5 |  |
| 666 | 2026-09-30T23:04:47Z | batch24-25: grcapx, grcapx3y, cfp, dNoa, roaq | critical 0, major 2, minor 2, low 2 |  |
| 669 | 2026-09-30T23:12:47Z | final batch: TotalAccruals, TrendFactor, VarCF, zerotrade1M, zerotrade6M, zerotrade12M | critical 0, major 0, minor 2, low 3 | clear_to_screen |
| 992 | 2026-10-01T09:05:04Z | STreversal@run032_rung5 (trigger: residual IC share 1.06) | critical 0, major 0, minor 0, low 2 | clear_to_apply |
| 1069 | 2026-10-01T17:14:30Z | 41edba9 D7 construction layer | major 1, medium 1, low 5 | fix first |
| 1084 | 2026-10-01T19:44:00Z | whole model v14 (19 legs, composite.py) before stop-and-ask 3/5 | critical 0, major 2, minor 4 | clean to take to the owner |
