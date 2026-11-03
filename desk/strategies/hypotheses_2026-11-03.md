# Hypotheses — 2026-11-03 (Quant v1)

Data: Alpaca SIP QQQ 1-min, split-adjusted, regular hours only, 2703 full sessions (21 half-days/partial sessions dropped).
IS 2016-01-04..2021-12-31 | OOS 2022-01-03..2026-11-02. Rules fixed in advance, NO parameter search. Costs: 1.5 bp round trip (ESTIMATE); stress = 1 bar late + 2x costs.
Trials counted for deflated Sharpe: 25 (11 bases + 3 ablations + 11 stress reruns). Code: desk/research/backtest_v1.py, raw output results_v1.json.

Limitations: no NQ/MNQ futures data (QQQ only, so overnight futures moves are invisible); no historical tier-1 event calendar, so the event filter is NOT applied in backtests; walk-forward = per-year results of fixed rules (nothing re-fit).

| # | Hypothesis | Type | IS Sharpe | OOS Sharpe | OOS stress | OOS trades | OOS avg bp | Score /25 | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H1_gap_fade | Opening gaps >0.5% overshoot and partly fill by the close. | Intraday | -0.27 | 0.11 | -0.11 | 552 | 1.34 | 12 | 0.001 | KILLED |
| H2_gap_go | Opening gaps >0.5% continue (opposite of H1, tested as its own trial). | Intraday | 0.06 | -0.36 | -0.4 | 552 | -4.34 | 10 | 0.0 | KILLED |
| H3_orb30 | A break of the first 30-min range keeps going. | Intraday | -0.66 | 0.72 | 0.43 | 1199 | 3.85 | 17 | 0.043 | KILLED |
| H4_first30_last30 | Prior close->10:00 return predicts the 15:30-16:00 return (intraday momentum). | Intraday | -0.37 | -1.27 | -1.97 | 1204 | -2.46 | 9 | 0.0 | KILLED |
| H5_overnight | Most index return comes overnight (close->open). | Swing (overnight) | 0.83 | 0.41 | 0.26 | 1205 | 2.26 | 15 | 0.01 | KILLED |
| H6_bigdown_3d | After a -2% day, QQQ bounces over the next 3 days. | Swing 1-5d | 0.46 | 0.85 | 0.75 | 75 | 62.88 | 18 | 0.085 | SURVIVES (provisional) |
| H7_rsi2_trend | Short pullbacks in an uptrend revert. | Swing 1-5d | 0.09 | 0.74 | 0.71 | 44 | 57.27 | 16 | 0.053 | KILLED |
| H8_vwap_fade | Stretches >2 sd from session VWAP revert to VWAP. | Intraday | -0.93 | -1.25 | -1.63 | 1184 | -4.7 | 9 | 0.0 | KILLED |
| H9_opex_week | Monthly OPEX week is bullish (dealer hedging/pinning). | Swing 1-5d | 0.55 | -0.16 | -0.2 | 55 | -13.82 | 7 | 0.0 | KILLED |
| H10_turn_of_month | Turn-of-month inflows (pensions, 401k) lift prices. | Swing 1-5d | 0.57 | 0.38 | 0.36 | 58 | 29.19 | 12 | 0.009 | KILLED |
| H11_lateday_mom | A >1% move by 14:00 continues into the close. | Intraday | 0.15 | 0.76 | 0.61 | 437 | 4.53 | 15 | 0.06 | KILLED |

## Details

### H1_gap_fade
- Thesis: Opening gaps >0.5% overshoot and partly fill by the close.
- Economic reason: Overnight liquidity is thin; retail/news-driven opens overreact.
- Who loses: Late chasers who buy/sell the open.
- Rules: Gap >0.5% vs prior close -> fade at 09:30 open, exit 16:00 close.
- Holding: Intraday

### H2_gap_go
- Thesis: Opening gaps >0.5% continue (opposite of H1, tested as its own trial).
- Economic reason: Gaps carry information that is absorbed during the day.
- Who loses: Gap faders.
- Rules: Gap >0.5% -> trade in gap direction at 09:30, exit 16:00.
- Holding: Intraday

### H3_orb30
- Thesis: A break of the first 30-min range keeps going.
- Economic reason: Range break triggers stops and trend-follower flow.
- Who loses: Range traders whose stops get run.
- Rules: First break of 09:30-10:00 high/low -> enter next bar, stop at other side of range, exit 16:00.
- Holding: Intraday

### H4_first30_last30
- Thesis: Prior close->10:00 return predicts the 15:30-16:00 return (intraday momentum).
- Economic reason: Late-day hedging/rebalancing by levered ETFs and informed traders.
- Who loses: Liquidity providers into the close.
- Rules: Sign of prior close->10:00 return -> trade 15:30-16:00.
- Holding: Intraday

### H5_overnight
- Thesis: Most index return comes overnight (close->open).
- Economic reason: Holding-period risk premium for carrying gap risk overnight.
- Who loses: Intraday-only traders who flatten.
- Rules: Buy 16:00 close, sell 09:30 open, every day.
- Holding: Swing (overnight)

### H6_bigdown_3d
- Thesis: After a -2% day, QQQ bounces over the next 3 days.
- Economic reason: Forced de-risking (vol-target funds, margin calls) overshoots; short-term liquidity premium.
- Who loses: Forced sellers and late panic sellers.
- Rules: Daily close-to-close < -2% -> buy next day 09:30 open, exit close of 3rd day.
- Holding: Swing 1-5d

### H7_rsi2_trend
- Thesis: Short pullbacks in an uptrend revert.
- Economic reason: Liquidity provision to short-term sellers inside a bull trend.
- Who loses: Short-term momentum sellers.
- Rules: RSI(2)<10 and close>200dma -> buy next open; exit next open after close>5dma, max 5 days.
- Holding: Swing 1-5d

### H8_vwap_fade
- Thesis: Stretches >2 sd from session VWAP revert to VWAP.
- Economic reason: Execution algos benchmark to VWAP and lean against stretches.
- Who loses: Momentum traders entering late.
- Rules: After 10:30, |close/VWAP-1| > 2x running sd -> fade next bar, exit at VWAP touch or 15:54.
- Holding: Intraday

### H9_opex_week
- Thesis: Monthly OPEX week is bullish (dealer hedging/pinning).
- Economic reason: Dealer gamma hedging and vanna/charm flows into expiry.
- Who loses: Put holders as options decay.
- Rules: Buy Monday open of OPEX week, sell OPEX Friday close.
- Holding: Swing 1-5d

### H10_turn_of_month
- Thesis: Turn-of-month inflows (pensions, 401k) lift prices.
- Economic reason: Scheduled cash inflows at month start.
- Who loses: Sellers into month-end flows.
- Rules: Buy open of last trading day of month, sell close of 3rd trading day of new month.
- Holding: Swing 1-5d

### H11_lateday_mom
- Thesis: A >1% move by 14:00 continues into the close.
- Economic reason: Levered/inverse ETF rebalancing buys strength/sells weakness into the close.
- Who loses: Counter-trend traders and the rebalanced ETF holders.
- Rules: |prior close->14:00| >1% -> trade in that direction 14:00-16:00.
- Holding: Intraday
