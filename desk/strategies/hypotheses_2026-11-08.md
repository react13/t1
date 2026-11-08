# Hypotheses — 2026-11-08 (Quant v6: intraday/calendar)

No new market data since Fri (data through 2026-11-06). Same engine/costs. Rules fixed before running. Cumulative trials: 141.

| # | Rule | IS Sharpe (trades) | OOS Sharpe (trades) | OOS stress | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|
| Q1 | Down >1.5% from open by 15:00 -> long 15:00 to close | -0.26 (79) | -1.04 (90) | -1.25 | 7 | 0.0 | KILLED |
| Q2 | Up >1.5% from open by 15:00 -> short 15:00 to close | 0.17 (55) | -0.96 (69) | -1.0 | 7 | 0.0 | KILLED |
| Q3 | First 15 min move >0.5% -> fade until 11:00 | -0.32 (169) | 0.52 (185) | 0.35 | 15 | 0.002 | KILLED |
| Q4 | After an inside day that closed up, long next open->close | -0.14 (79) | -0.09 (66) | -0.15 | 8 | 0.0 | KILLED |
| Q5 | After 3 up days, short next open->close | -0.16 (278) | -0.37 (200) | -0.47 | 8 | 0.0 | KILLED |
| Q6 | After 3 down days, long next open->close | 0.31 (89) | 0.81 (106) | 0.78 | 17 | 0.007 | KILLED |
| Q7 | Close in top 10% of day range -> hold overnight | -0.04 (296) | 0.12 (199) | -0.1 | 12 | 0.0 | KILLED |
| Q8 | Thanksgiving week: long Mon open -> Wed close | -0.04 (6) | 0.72 (4) | 0.7 | 14 | 0.001 | KILLED |
| Q9 | First trading day of the month: long open->close | 0.29 (71) | 0.19 (59) | 0.1 | 11 | 0.0 | KILLED |
| Q10 | Break of the 09:30-12:00 high after 12:00 -> long to close, stop at morning low | 0.1 (723) | 0.68 (566) | 0.42 | 17 | 0.003 | KILLED |

Closest: Q6 (3 down days -> long next day, 17/25, OOS 0.81 but IS only 0.31 on 89 trades) and Q10 (midday breakout, 17/25, IS 0.10). Both look like the same 'buy weakness' family as H6, not new edges.

Multiple testing: 141 cumulative trials. See questions.md #5.