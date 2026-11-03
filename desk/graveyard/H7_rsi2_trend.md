# H7_rsi2_trend — KILLED 2026-11-03 (score 16/25)
- Rules: RSI(2)<10 and close>200dma -> buy next open; exit next open after close>5dma, max 5 days.
- IS Sharpe 0.09 | OOS Sharpe 0.74 | OOS stress 0.71 | DSR 0.053
- Score: {'sharpe': '3', 'drawdown': '4', 'trades': 2, 'edge': '4', 'wf': '3', 'total': '16', 'years_pos_pct': 64}
- Years: {'2016': -0.84, '2017': 3.21, '2018': -2.85, '2019': 1.91, '2020': -3.43, '2021': 6.16, '2022': -3.95, '2023': 1.96, '2024': 15.55, '2025': 6.78, '2026': 4.86}
- Reason: few OOS trades (44); ablation: no_trend_filter: IS -0.13 / OOS 0.85
