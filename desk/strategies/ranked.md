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
