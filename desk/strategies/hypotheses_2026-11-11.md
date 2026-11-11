# Hypotheses — 2026-11-11 (Quant v10: intraday ideas that FIT 1 MNQ, 0.54% stop ~ $300/contract)

Data through 2026-11-10. Costs 1.5 bp + 1 bp stop slippage. Rules fixed before running. Cumulative trials: 213.

| # | Rule | IS Sharpe (trades) | OOS Sharpe (trades) | OOS stress | Avg $/MNQ OOS | Worst $/MNQ | Score | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| M1 | 30-min opening-range breakout, 0.54% stop | -0.49 (1489) | 0.19 (1205) | -0.14 | 4.9 | -315.0 | 12 | 0.001 | KILLED |
| M2 | Gap >0.5% fade, 0.54% stop | -0.27 (519) | 0.4 (556) | 0.1 | 19.4 | -315.0 | 13 | 0.004 | KILLED |
| M3 | Gap down >0.5% buy, 0.54% stop | 0.32 (214) | 0.05 (261) | -0.19 | 3.3 | -315.0 | 13 | 0.0 | KILLED |
| M4 | First 30 min >0.2% -> follow 10:00-close, 0.54% stop | 0.47 (813) | 0.25 (748) | -0.16 | 8.4 | -315.0 | 15 | 0.002 | KILLED |
| M5 | Prior close->14:00 >1% -> follow to close, 0.54% stop | -0.22 (414) | 0.04 (442) | -0.16 | 1.0 | -315.0 | 12 | 0.0 | KILLED |
| M6 | First 5 min >0.3% -> follow to close, 0.54% stop | -0.29 (148) | 0.66 (234) | 0.59 | 64.6 | -315.0 | 17 | 0.008 | KILLED |
| M7 | Day after a -2% day: long open->close, 0.54% stop | 0.11 (84) | -0.44 (91) | -0.76 | -59.5 | -315.0 | 7 | 0.0 | KILLED |
| M8 | After -1% day + gap down >0.3%: long open->close, 0.54% stop | 0.42 (58) | 0.13 (77) | -0.14 | 20.9 | -315.0 | 12 | 0.001 | KILLED |
| M9 | Below VWAP 10:00-11:00 then reclaims it by 15:00 -> long to close, 0.54% stop | -0.13 (121) | -0.24 (99) | -0.29 | -21.2 | -315.0 | 7 | 0.0 | KILLED |
| M10 | Break of 09:30-12:00 high after 12:00 -> long to close, 0.54% stop | 0.12 (723) | -0.0 (567) | -0.38 | -0.0 | -315.0 | 10 | 0.0 | KILLED |

Result: no intraday rule with a ~$300/contract stop survived. Closest: M6 opening drive (17/25) — IS -0.29 vs OOS 0.66 = regime flip, not stable.
Implication for MNQ: the desk has NO strategy that both has an edge and fits 1 MNQ inside $350/day. See question #6.