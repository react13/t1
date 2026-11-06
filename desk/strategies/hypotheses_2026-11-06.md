# Hypotheses — 2026-11-06 (Quant v4: risk variants of the approved strategies)

Data through 2026-11-05 incl. the Nov 5 -6.37% day. Same engine/costs. Rules fixed before running. Cumulative trials: 101.
Base for comparison: I3 OOS Sharpe 0.94 (max DD 14.3%), H6 OOS 0.84 (max DD 9.4%).

| Variant | Rule | IS Sharpe | OOS Sharpe | OOS stress | OOS trades | OOS max DD % | 2020 % | 2022 % | Score | DSR |
|---|---|---|---|---|---|---|---|---|---|---|
| R1_h6_moderate_drops | H6 only when the drop is between -2% and -5% (skip extreme days). | 0.52 | 0.98 | 0.88 | 74 | 9.42 | 7.88 | 24.35 | 19 | 0.035 |
| R2_h6_extreme_drops | H6 only after drops of -4% or worse. | -0.03 | -0.3 | -0.37 | 10 | 13.14 | -2.16 | -0.92 | 5 | 0.0 |
| R3_h6_volscaled | H6 sized by (IS median 20-day vol / current 20-day vol), capped at 2x. | 0.67 | 0.91 | 0.82 | 76 | 6.15 | 4.31 | 7.74 | 17 | 0.026 |
| R4_i3_skip_highvol | I3 but skip nights when 20-day vol > 2x its IS median. | 1.24 | 1.06 | 0.72 | 871 | 10.94 | 17.3 | -2.18 | 22 | 0.061 |
| R5_i3_volscaled | I3 sized by (IS median 20-day vol / current), capped at 2x. | 1.11 | 1.21 | 0.81 | 901 | 8.22 | 13.68 | -3.53 | 22 | 0.106 |
| R6_i3_skip_after_-3pct | I3 but skip the night after a -3% or worse day. | 1.1 | 0.87 | 0.53 | 893 | 13.86 | 19.83 | -6.18 | 19 | 0.024 |
| R7_h6_no_cluster | H6 but skip if another -2% day happened in the prior 5 sessions. | 0.91 | 0.65 | 0.58 | 44 | 6.08 | 13.29 | 6.05 | 16 | 0.005 |
| R8_i3_ma100 | I3 with a 100-day average instead of 200 (neighbour check). | 0.98 | 1.05 | 0.72 | 834 | 16.26 | 26.44 | -8.29 | 22 | 0.056 |
| R9_i3_ma50 | I3 with a 50-day average (neighbour check). | 1.04 | 0.72 | 0.47 | 791 | 17.78 | 27.42 | -8.32 | 18 | 0.01 |
| R10_combo_i3_h6 | I3 + H6 run together at equal 1x notional (portfolio view). | 0.98 | 1.19 | 0.91 | 977 | 15.7 | 27.39 | 15.77 | 23 | 0.098 |

## H6 trades after <= -4% days (signal date, drop %, 3-day trade %)

- 2018-02-08: -4.21% -> 2.58%
- 2018-10-10: -4.36% -> 0.63%
- 2018-10-24: -4.65% -> -2.54%
- 2020-02-27: -5.0% -> 5.38%
- 2020-03-09: -6.94% -> -11.86%
- 2020-03-11: -4.38% -> -6.87%
- 2020-03-12: -9.24% -> -2.67%
- 2020-03-16: -12.57% -> 1.33%
- 2020-04-01: -4.24% -> 8.27%
- 2020-06-11: -4.91% -> 1.61%
- 2020-09-03: -5.13% -> -2.79%
- 2020-09-08: -4.74% -> -1.84%
- 2022-02-03: -4.05% -> 1.44%
- 2022-04-29: -4.48% -> 5.41%
- 2022-05-05: -4.96% -> -3.26%
- 2022-05-18: -4.95% -> 1.43%
- 2022-06-13: -4.57% -> -2.18%
- 2022-08-26: -4.09% -> -1.76%
- 2022-09-13: -5.52% -> -1.91%
- 2025-04-03: -5.35% -> -5.0%
- 2025-04-04: -6.1% -> 13.82%
- 2025-04-10: -4.07% -> 3.0%
- 2026-06-05: -4.76% -> -3.35%