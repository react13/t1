# Hypotheses — 2026-11-10 (Quant v8)

Data through 2026-11-09. Same engine/costs. Rules fixed before running. Cumulative trials: 181.

| # | Rule | IS Sharpe (trades) | OOS Sharpe (trades) | OOS stress | 2022 % | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|
| U1 | Day after a +3% day: long open->close (continuation) | -0.72 (23) | 0.09 (27) | 0.1 | 3.43 | 8 | 0.0 | KILLED |
| U2 | Day after a +3% day: short open->close (fade) | 0.69 (23) | -0.14 (27) | -0.19 | -3.97 | 5 | 0.0 | KILLED |
| U3 | Overnight hold after a +2% day | -0.43 (57) | -0.45 (91) | -0.51 | -12.0 | 7 | 0.0 | KILLED |
| U4 | Close within 1% below the 200-day avg -> long 3 days | 0.18 (8) | 0.2 (11) | 0.17 | -8.92 | 8 | 0.0 | KILLED |
| U5 | Gap up >1% after a down week -> long open->close | 0.93 (57) | -0.14 (75) | -0.18 | 2.06 | 10 | 0.0 | KILLED |
| U6 | Prior week > +2% -> long Mon open to Fri close | -0.03 (71) | 0.3 (69) | 0.22 | -12.2 | 11 | 0.001 | KILLED |
| U7 | Prior week < -2% -> long Monday open->close only | -0.02 (38) | 0.93 (58) | 0.82 | 5.29 | 17 | 0.03 | KILLED |
| U8 | Close back above 20-day avg after 5 days below -> long 3 days | 0.29 (26) | 0.82 (27) | 0.79 | 1.38 | 15 | 0.017 | KILLED |
| U9 | Close below 20-day avg after 10 days above -> short 3 days | 0.04 (36) | -0.55 (25) | -0.53 | -3.11 | 5 | 0.0 | KILLED |
| U10 | I3 but only Mon-Wed nights | 1.29 (722) | 1.09 (543) | 0.75 | -3.4 | 22 | 0.07 | I3 VARIANT (noted, not proposed) |