# Hypotheses — 2026-11-05 (Quant v3)

Data through 2026-11-04 (2705 sessions). Same engine, 1.5 bp RT costs (ESTIMATE). Rules fixed in advance.
Cumulative trials v1-v3: 81. Code: desk/research/backtest_v3.py, results_v3.json.

| # | Hypothesis | Type | IS Sharpe | OOS Sharpe | OOS stress | OOS trades | 2020 % | 2022 % | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1_h6_uptrend | H6 only when QQQ is above its 200-day average. | Swing 3d | 0.82 | 0.61 | 0.59 | 33 | 17.88 | -2.84 | 16 | 0.101 | KILLED |
| F2_h6_downtrend | H6 only when QQQ is below its 200-day average. | Swing 3d | -0.12 | 0.63 | 0.52 | 43 | -11.57 | 25.27 | 13 | 0.101 | KILLED |
| F3_h6_gapdown_confirm | H6 only if the next open gaps down further. | Swing 3d | 0.19 | 0.48 | 0.39 | 39 | 19.46 | 25.06 | 12 | 0.055 | KILLED |
| F4_h6_moc_entry | H6 signal from 15:50 price, buy at that day's close instead of next open. | Swing 3d | 0.81 | -0.01 | 0.03 | 71 | 20.33 | 0.0 | 9 | 0.004 | KILLED |
| F5_h6_first_profit_exit | H6 but exit at the first close above entry (max 3 days). | Swing 1-3d | 1.27 | 0.35 | 0.21 | 80 | 38.98 | 5.91 | 14 | 0.03 | KILLED |
| I1_month_last_day | Last trading day of the month: long open->close. | Intraday | -0.07 | 0.18 | 0.14 | 58 | 3.6 | 2.42 | 10 | 0.011 | KILLED |
| I2_morning_flush_reversal | Down >1.5% vs prior close by 11:00 -> long 11:00 to close. | Intraday | -0.16 | -0.12 | -0.22 | 97 | -16.44 | -3.03 | 7 | 0.002 | KILLED |
| I3_overnight_uptrend | Hold QQQ overnight (close -> next open) only while it closes above its 200-day average. | Swing (overnight) | 1.12 | 0.97 | 0.65 | 900 | 21.08 | -6.66 | 21 | 0.316 | SURVIVES (provisional) |
| I4_turnaround_tuesday | After a down Monday, long Tuesday open->close. | Intraday | 1.04 | -0.06 | -0.15 | 84 | -0.27 | -10.56 | 10 | 0.003 | KILLED |
| I5_inside_day_breakout | After an inside day, trade the first break of its high/low, stop at the other side, exit at close. | Intraday | 0.13 | -0.15 | -0.26 | 119 | 9.13 | -14.88 | 8 | 0.002 | KILLED |

## Details

### F1_h6_uptrend
- Thesis: H6 only when QQQ is above its 200-day average.
- Economic reason: Dips in uptrends are bought faster.
- Who loses: Forced sellers in a bull market.
- Holding: Swing 3d

### F2_h6_downtrend
- Thesis: H6 only when QQQ is below its 200-day average.
- Economic reason: Bear-market rallies are violent.
- Who loses: Shorts squeezed after flushes.
- Holding: Swing 3d

### F3_h6_gapdown_confirm
- Thesis: H6 only if the next open gaps down further.
- Economic reason: Capitulation confirmation.
- Who loses: Overnight panic sellers.
- Holding: Swing 3d

### F4_h6_moc_entry
- Thesis: H6 signal from 15:50 price, buy at that day's close instead of next open.
- Economic reason: Capture the overnight bounce too.
- Who loses: Same as H6.
- Holding: Swing 3d

### F5_h6_first_profit_exit
- Thesis: H6 but exit at the first close above entry (max 3 days).
- Economic reason: Take the bounce quickly.
- Who loses: Same as H6.
- Holding: Swing 1-3d

### I1_month_last_day
- Thesis: Last trading day of the month: long open->close.
- Economic reason: Month-end rebalancing/window dressing inflows.
- Who loses: Sellers into month-end.
- Holding: Intraday

### I2_morning_flush_reversal
- Thesis: Down >1.5% vs prior close by 11:00 -> long 11:00 to close.
- Economic reason: Morning liquidation overshoots.
- Who loses: Morning panic sellers.
- Holding: Intraday

### I3_overnight_uptrend
- Thesis: Hold QQQ overnight (close -> next open) only while it closes above its 200-day average.
- Economic reason: Overnight risk premium (H5) is earned mostly in uptrends; in downtrends overnight gap risk is not paid.
- Who loses: Intraday-only traders and those who flatten overnight; hedgers paying for overnight protection.
- Holding: Swing (overnight)

### I4_turnaround_tuesday
- Thesis: After a down Monday, long Tuesday open->close.
- Economic reason: Weekend-news overreaction reverses.
- Who loses: Monday sellers.
- Holding: Intraday

### I5_inside_day_breakout
- Thesis: After an inside day, trade the first break of its high/low, stop at the other side, exit at close.
- Economic reason: Compression precedes expansion.
- Who loses: Range traders.
- Holding: Intraday
