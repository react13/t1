# H8_vwap_fade — KILLED 2026-11-03 (score 9/25)
- Rules: After 10:30, |close/VWAP-1| > 2x running sd -> fade next bar, exit at VWAP touch or 15:54.
- IS Sharpe -0.93 | OOS Sharpe -1.25 | OOS stress -1.63 | DSR 0.0
- Score: {'sharpe': '1', 'drawdown': '1', 'trades': 5, 'edge': '1', 'wf': '1', 'total': '9', 'years_pos_pct': 0}
- Years: {'2016': -1.4, '2017': -4.02, '2018': -15.68, '2019': -7.99, '2020': -3.25, '2021': -9.15, '2022': -27.3, '2023': -6.6, '2024': -7.86, '2025': -13.06, '2026': -0.82}
- Reason: OOS Sharpe -1.25 (no edge out of sample); only 0% of years positive; ablation: no_time_filter: IS -0.87 / OOS -0.91
