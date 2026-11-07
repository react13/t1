# Hypotheses — 2026-11-07 (Quant v5: high-vol regime)

Data through 2026-11-06. Same engine/costs. Rules fixed before running. Cumulative trials: 121.

| # | Rule | IS Sharpe (trades) | OOS Sharpe (trades) | OOS stress | 2020 % | 2022 % | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Follow-through: day after a +1% bounce that followed a <=-4% day, long open->close | -0.32 (7) | -0.74 (4) | -0.68 | -6.1 | -0.87 | 5 | 0.0 | KILLED |
| P2 | Fade the first up day after a <=-4% day (short next open->close) | -0.12 (9) | 0.71 (7) | 0.66 | -0.39 | 0.59 | 13 | 0.0 | KILLED |
| P3 | Weekly reversal: week < -4% -> long Mon open to Fri close | 0.43 (12) | 0.72 (17) | 0.7 | 11.46 | 18.61 | 14 | 0.012 | KILLED |
| P4 | Short overnight when below 200-day avg AND 20-day vol > 1.5x normal | -0.07 (83) | 0.27 (296) | -0.05 | -1.34 | 15.29 | 12 | 0.002 | KILLED |
| P5 | High vol + gap-down >1% -> long open->close | 0.58 (44) | -0.07 (67) | -0.18 | -0.32 | -4.04 | 7 | 0.0 | KILLED |
| P6 | High vol + gap-up >1% -> short open->close | -0.8 (67) | -0.14 (69) | -0.12 | -18.29 | -7.29 | 7 | 0.0 | KILLED |
| P7 | First close below 200-day in 50 sessions -> short 5 days | 0.26 (3) | 0.96 (3) | 0.96 | 15.66 | 5.11 | 15 | 0.013 | KILLED |
| P8 | Close back above 200-day after 10+ sessions below -> long 5 days | 0.04 (3) | 0.49 (5) | 0.48 | 5.46 | -2.22 | 9 | 0.006 | KILLED |
| P9 | High vol: short Fri close -> Mon open | -0.19 (61) | 0.25 (79) | 0.05 | 3.34 | 10.3 | 10 | 0.001 | KILLED |
| P10 | Late-day momentum (H11) only when vol is not high | -0.53 (225) | 0.02 (211) | -0.22 | -1.81 | 0.78 | 11 | 0.0 | KILLED |

Why none survived: the extreme-day rules (P1, P2, P7, P8) have 3-17 trades, too few to judge; the high-vol gap rules (P5, P6) lose OOS.