# H3_orb30 — KILLED 2026-11-03 (score 17/25)
- Rules: First break of 09:30-10:00 high/low -> enter next bar, stop at other side of range, exit 16:00.
- IS Sharpe -0.66 | OOS Sharpe 0.72 | OOS stress 0.43 | DSR 0.043
- Score: {'sharpe': '3', 'drawdown': '4', 'trades': 5, 'edge': '3', 'wf': '2', 'total': '17', 'years_pos_pct': 55}
- Years: {'2016': -6.13, '2017': -5.8, '2018': -8.54, '2019': 0.64, '2020': -30.39, '2021': 5.1, '2022': 20.53, '2023': 10.62, '2024': 11.15, '2025': 11.29, '2026': -7.4}
- Reason: IS Sharpe -0.66 vs OOS 0.72: regime flip, unstable; only 55% of years positive; ablation: no_stop: IS -1.19 / OOS 0.67
