# Hypotheses — 2026-11-04 (Quant v2)

Data refreshed through 2026-11-03 (2704 full sessions). Same engine, 1.5 bp RT costs (ESTIMATE), rules fixed in advance, no tuning.
Cumulative trials across v1+v2: 61 (v1 25 + 10 new bases + 10 stress reruns + 16-cell H6 grid). Code: desk/research/backtest_v2.py, results_v2.json.

| # | Hypothesis | Type | IS Sharpe | OOS Sharpe | OOS stress | OOS trades | Score /25 | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| N1_gapdown_after_down | After a < -1% day, a further gap down of >0.3% gets bought: long open->close. | Intraday | 0.85 | 0.53 | 0.33 | 77 | 17 | 0.088 | KILLED |
| N2_two_down_streak | Two down closes totalling < -2% bounce over 3 days. | Swing 3d | 0.39 | 0.58 | 0.52 | 88 | 16 | 0.114 | KILLED |
| N3_nr7_orb | Opening-range breakout works after an NR7 (narrowest 7-day range) day. | Intraday | 0.49 | 0.45 | 0.36 | 180 | 14 | 0.065 | KILLED |
| N4_weekend | Holding Fri close -> Mon open earns a weekend risk premium. | Swing (weekend) | -0.04 | 0.1 | 0.17 | 214 | 12 | 0.015 | KILLED |
| N5_lunch_fade | The 10:00->12:00 move (>0.2%) reverses 12:00->14:00. | Intraday | -0.6 | -0.03 | -0.38 | 865 | 9 | 0.007 | KILLED |
| N6_close_at_low_bounce | A close in the bottom 10% of the day's range bounces next day open->close. | Intraday | 0.9 | 0.33 | 0.14 | 131 | 15 | 0.041 | KILLED |
| N7_bigup_fade | After a > +2% day, fade for 3 days (mirror of H6). | Swing 3d | 0.22 | -0.32 | -0.34 | 73 | 7 | 0.001 | KILLED |
| N8_opening_drive | First 5-min move >0.3% continues to 10:30. | Intraday | -0.5 | 0.26 | 0.13 | 232 | 11 | 0.032 | KILLED |
| N9_pre_holiday | Day before a weekday market holiday drifts up. | Intraday | -0.09 | 0.28 | 0.16 | 48 | 9 | 0.035 | KILLED |
| N10_overnight_after_down | Buy the close of a < -1% day, sell next open. | Swing (overnight) | 0.29 | 0.42 | 0.53 | 243 | 15 | 0.069 | KILLED |

## Details

### N1_gapdown_after_down
- Thesis: After a < -1% day, a further gap down of >0.3% gets bought: long open->close.
- Economic reason: Capitulation at the open; dip buyers step in.
- Who loses: Panic sellers at the open.
- Holding: Intraday

### N2_two_down_streak
- Thesis: Two down closes totalling < -2% bounce over 3 days.
- Economic reason: Short-term overshoot, like H6 but slower.
- Who loses: Forced sellers.
- Holding: Swing 3d

### N3_nr7_orb
- Thesis: Opening-range breakout works after an NR7 (narrowest 7-day range) day.
- Economic reason: Volatility compression precedes expansion.
- Who loses: Range sellers.
- Holding: Intraday

### N4_weekend
- Thesis: Holding Fri close -> Mon open earns a weekend risk premium.
- Economic reason: Pay for carrying weekend gap risk.
- Who loses: Traders who flatten before weekends.
- Holding: Swing (weekend)

### N5_lunch_fade
- Thesis: The 10:00->12:00 move (>0.2%) reverses 12:00->14:00.
- Economic reason: Thin lunch liquidity mean-reverts morning flows.
- Who loses: Late morning chasers.
- Holding: Intraday

### N6_close_at_low_bounce
- Thesis: A close in the bottom 10% of the day's range bounces next day open->close.
- Economic reason: MOC selling imbalances overshoot.
- Who loses: Closing-auction sellers.
- Holding: Intraday

### N7_bigup_fade
- Thesis: After a > +2% day, fade for 3 days (mirror of H6).
- Economic reason: Short-covering rallies overshoot.
- Who loses: Late buyers.
- Holding: Swing 3d

### N8_opening_drive
- Thesis: First 5-min move >0.3% continues to 10:30.
- Economic reason: Opening order imbalance takes time to clear.
- Who loses: Faders of the open.
- Holding: Intraday

### N9_pre_holiday
- Thesis: Day before a weekday market holiday drifts up.
- Economic reason: Light volume + positive sentiment; documented calendar effect.
- Who loses: Short sellers covering into the holiday.
- Holding: Intraday

### N10_overnight_after_down
- Thesis: Buy the close of a < -1% day, sell next open.
- Economic reason: Overnight premium is larger after stress.
- Who loses: Intraday sellers who won't hold overnight.
- Holding: Swing (overnight)
