# N6_close_at_low_bounce — KILLED 2026-11-04 (score 15/25)
- Thesis: A close in the bottom 10% of the day's range bounces next day open->close.
- IS Sharpe 0.9 | OOS 0.33 | stress 0.14 | DSR 0.041
- Score: {'sharpe': '2', 'drawdown': '3', 'trades': 4, 'edge': '2', 'wf': '4', 'total': '15', 'years_pos_pct': 82}
- Years: {'2016': 6.47, '2017': 5.63, '2018': -0.34, '2019': 1.46, '2020': 18.17, '2021': 2.89, '2022': 9.76, '2023': 2.55, '2024': 1.99, '2025': 2.16, '2026': -4.94}
- Reason: OOS decay IS 0.9 -> OOS 0.33; fragile to 1 bar late + 2x costs (OOS 0.33 -> 0.14); score 15/25 < 18
