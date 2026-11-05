# Ranked strategies (updated Quant v3, 2026-11-05)
Two provisional strategies. Neither is statistically proven after deflation (81 trials). Paper probe only.

## 1. I3_overnight_uptrend — score 21/25 — PROVISIONAL (NEW)
- Rules: at each close, if QQQ's close > its 200-day simple average, buy at the close (MOC) and sell at the next 09:30 open (MOO). Otherwise stay flat.
  MNQ equivalent: hold 16:00 -> 09:30 ET on days the filter is on.
- Thesis: the overnight risk premium is paid in uptrends; in downtrends overnight gaps are not compensated. Who loses: intraday-only traders and
  overnight hedgers.
- Score: Sharpe 3 | Drawdown 4 | Trades 5 | Edge 4 | Walk-forward 5 (91% of years positive)
- IS 2016-2021: Sharpe 1.12, 1201 nights, avg 5.51 bp, win 59.2%, max DD 21.55%
- OOS 2022-2026: Sharpe 0.97, 900 nights, avg 5.24 bp, win 56.2%, max DD 14.34%, t 2.13
- Stress (1 bar late exit + 2x costs) OOS: Sharpe 0.65.
- COST SENSITIVITY (key risk, ~250 round trips/yr): OOS Sharpe 0.97 at 1.5 bp, 0.70 at 3 bp, 0.32 at 5 bp round trip.
  ESTIMATE of real cost: MNQ ~0.4 bp RT (commission + 1 tick/side); QQQ auctions ~0.2 bp + fees. Edge survives only if fills stay near auction prices.
- Ablation: drop the 200-day filter = H5_overnight: IS 0.83 / OOS 0.41 -> filter roughly doubles OOS edge. Keep it.
- Per year (% notional): {'2016': 3.22, '2017': 13.61, '2018': 4.49, '2019': 12.54, '2020': 21.08, '2021': 11.18, '2022': -6.66, '2023': 6.86, '2024': 26.9, '2025': 17.48, '2026': 2.62}. 2020 21.08% (survived), 2022 -6.66% (LOSS: failed the 2022 check).
- Monte Carlo 1,000 runs OOS: 95th pct max DD 26.48%, worst 47.41%.
- Deflated Sharpe (81 trials): 0.316 (needs 0.95) -> NOT significant.
- Final check: OOS yes | after costs yes | 1 bar late + 2x yes | ablation clean | 2020 yes / 2022 NO | DSR NO.

### WHY THIS COULD FAIL
- Costs: at 5 bp round trip most of the edge is gone; auction fills or MNQ roll/spread costs above estimate kill it.
- 2022-style grinding bear markets that whipsaw around the 200-day average (it lost 6.7% in 2022).
- Overnight gap risk on news (elections, earnings of mega-caps) — exactly what the premium pays for; one large gap can take months of edge.
- Well-known anomaly (overnight drift) -> may be crowded and decaying.

## 2. H6_bigdown_3d — 18/25 — PROVISIONAL (refreshed through 2026-11-04)
- OOS now: Sharpe 0.84, 76 trades, avg 61.38 bp. DSR 0.212 with 81 trials.
- v3 filter tests: none of 5 filters beats plain H6 (uptrend-only 0.61, downtrend-only 0.63, gap-confirm 0.48, first-profit exit 0.35).
- FRAGILITY found: entering at the signal day's close instead of the next open (F4) gives OOS Sharpe -0.01. The edge depends on the
  next-open entry, i.e. on the gap after a down day. Any change to entry timing must be re-tested.
- Earlier detail (v1 write-up, v2 robustness grid) kept below.


---
# Previous versions
# Ranked strategies (Quant v1, 2026-11-03)
Only one hypothesis reached 18/25, and only just. It is NOT statistically proven after deflation; treat as a paper-only probe.

## 1. H6_bigdown_3d — score 18/25 — PROVISIONAL (paper probe only)
- Rules: QQQ daily close-to-close return < -2% -> buy next day at the 09:30 open -> exit at the close of the 3rd trading day (incl. entry day).
  One position at a time. Signal researched on QQQ (no MNQ data yet).
- Thesis: forced de-risking after a big down day overshoots. Who loses: forced/panic sellers.
- Score: Sharpe 3 | Drawdown 5 | Trades 3 | Edge 3 | Walk-forward 4
- IS 2016-2021: Sharpe 0.46, 68 trades, avg 51.5 bp, win 64.7%, max DD 27.13% of notional
- OOS 2022-2026: Sharpe 0.85, 75 trades, avg 62.88 bp, win 54.7%, max DD 9.42%, t-stat 1.79
- Stress (1 bar late + 2x costs), OOS: Sharpe 0.75, avg 54.78 bp -> robust to execution.
- Per year (% of notional): {'2016': 1.13, '2017': 5.99, '2018': -3.57, '2019': 17.62, '2020': 6.31, '2021': 7.53, '2022': 22.43, '2023': 10.63, '2024': 3.85, '2025': -2.71, '2026': 12.97}. 2020 6.31%, 2022 22.43% -> survived both.
- Monte Carlo (1,000 bootstrap runs of OOS active days): 95th pct max DD 29.23%, worst 60.97% of notional.
- Deflated Sharpe (25 trials): probability 0.085 (needs >= 0.95). Benchmark Sharpe for luck alone ~1.47. -> NOT significant.
- Ablation: one rule only (the -2% trigger). Dropping it = buy-and-hold in 3-day blocks, which is a different strategy; no rule to delete.
- Tiered vs flat sizing: NOT TESTABLE yet (one strategy, no historical event calendar, no filter set). Per rules -> flat $100, and Probe $50 for first 2 weeks.
- Final check: OOS yes | after costs yes | 1 bar late + 2x slippage yes | ablation n/a | 2020 & 2022 yes | deflated Sharpe NO.

### WHY THIS COULD FAIL
- Edge is not significant after accounting for 25 trials (DSR 0.085); the 18/25 may be luck.
- Only ~15 trades a year; one bad cluster (e.g. 2008-style crash with many -2% days in a row) is not in the 2016-2026 sample.
- Bootstrap worst-case drawdown (60.97% of notional) is far above the realised 9.42%: falling-knife risk is real.
- 3-day holds go through overnight gaps and events; the backtest did not skip tier-1 events.
- QQQ != MNQ: futures trade overnight; signal and fills will differ slightly.


## Robustness update (Quant v2, 2026-11-04) — H6 parameter neighbourhood
16 nearby settings (trigger x hold days), same engine and costs. Fixed rules, not a search: the live rule stays -2% / 3 days.
| Trigger | Hold days | IS Sharpe | OOS Sharpe | OOS trades |
|---|---|---|---|---|
| -0.015 | 2 | 0.7 | 0.33 | 134 |
| -0.015 | 3 | 0.87 | 0.54 | 115 |
| -0.015 | 4 | 0.68 | 0.44 | 106 |
| -0.015 | 5 | 0.56 | 0.23 | 98 |
| -0.02 | 2 | 0.85 | 0.45 | 84 |
| -0.02 | 3 | 0.46 | 0.85 | 75 |
| -0.02 | 4 | 0.55 | 0.68 | 70 |
| -0.02 | 5 | 0.9 | 0.21 | 62 |
| -0.025 | 2 | 0.7 | -0.05 | 48 |
| -0.025 | 3 | 0.32 | 0.25 | 43 |
| -0.025 | 4 | 0.44 | 0.25 | 41 |
| -0.025 | 5 | 0.65 | -0.0 | 37 |
| -0.03 | 2 | 0.56 | -0.28 | 29 |
| -0.03 | 3 | 0.2 | -0.09 | 27 |
| -0.03 | 4 | 0.27 | 0.23 | 26 |
| -0.03 | 5 | 0.48 | -0.08 | 24 |

What this says:
- The live cell (-2%, 3 days) has the BEST OOS Sharpe of all 16 (0.85). Its neighbours are typically 0.2-0.7 -> the 0.85 is partly luck of the pick.
  Realistic OOS Sharpe to expect: ~0.4-0.5 (ESTIMATE, median of the -1.5% and -2% rows).
- IS Sharpe is positive in all 16 cells; OOS is positive in all 8 cells with triggers of -1.5% or -2%, and fades at -2.5%/-3% (fewer trades, 24-48).
  -> The 'buy after a down day' effect looks real but modest; deeper triggers do not add edge.
- Deflated Sharpe with 61 cumulative trials: 0.287 (needs 0.95) -> still NOT significant.
  (It rose vs v1's 0.085 because the 16 grid cells are highly correlated, which narrows the spread of trial Sharpes; it is not new evidence.)
- Verdict unchanged: PROVISIONAL, paper probe size only. Monitor live paper results against an OOS Sharpe of ~0.45, not 0.85.
