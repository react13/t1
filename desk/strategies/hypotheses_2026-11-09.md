# Hypotheses — 2026-11-09 (Quant v7)

Data through 2026-11-06. Same engine/costs. Rules fixed before running. Cumulative trials: 161.

| # | Rule | IS Sharpe (trades) | OOS Sharpe (trades) | OOS stress | 2022 % | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|
| T1 | I3 (overnight when above 200-day) but skip Friday nights | 1.33 (966) | 1.0 (721) | 0.62 | -4.11 | 20 | 0.053 | I3 VARIANT (noted, not proposed) |
| T2 | Overnight hold when close in bottom 30% of day range | 0.78 (312) | 0.69 (342) | 0.7 | -1.25 | 18 | 0.011 | SURVIVES (provisional challenger) |
| T3 | Gap up >0.3% and 10:00 price above open -> long 10:00 to close | 0.49 (260) | 0.23 (216) | 0.11 | 1.51 | 14 | 0.001 | KILLED |
| T4 | Lowest close in 5 days while above 200-day -> buy next open, hold 2 days | 0.37 (150) | 0.7 (136) | 0.68 | -8.34 | 17 | 0.011 | KILLED |
| T5 | Lowest close in 10 days while above 200-day -> buy next open, hold 5 days | 0.58 (52) | 0.77 (53) | 0.77 | -5.01 | 16 | 0.018 | KILLED |
| T6 | 5-minute opening-range breakout, stop at other side, exit close | -0.17 (1497) | 0.44 (1209) | 0.08 | 17.18 | 14 | 0.001 | KILLED |
| T7 | Monday after a down Friday: long open->close | 0.14 (126) | 0.81 (104) | 0.56 | 0.62 | 16 | 0.02 | KILLED |
| T8 | Every Tuesday: long open->close | 0.08 (308) | -0.09 (251) | -0.21 | -14.62 | 11 | 0.0 | KILLED |
| T9 | Every day: long the last hour (15:00-16:00) | -0.69 (1497) | -0.64 (1209) | -1.31 | 0.97 | 9 | 0.0 | KILLED |
| T10 | Every day: long the first hour (09:30-10:30) | 0.33 (1497) | -0.4 (1209) | -0.97 | -8.18 | 9 | 0.0 | KILLED |