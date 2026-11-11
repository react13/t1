# Ranked strategies (updated Quant v3, 2026-11-05)
Two provisional strategies. Neither is statistically proven after deflation (81 trials). Paper probe only.

## 1. I3_overnight_uptrend — score 21/25 — PROVISIONAL (NEW)
- Rules: at each close, if QQQ's close > its 200-day simple average, buy at the close (MOC) and sell at the next 09:30 open (MOO). Otherwise stay flat.
  MNQ equivalent: hold 16:00 -> 09:30 ET on days the filter is on.
- Thesis: the overnight risk premium is paid in uptrends; in downtrends overnight gaps are not compensated. Who loses: intraday-only traders and
  overnight hedgers.
- Score: Sharpe 3 | Drawdown 4 | Trades 5 | Edge 4 | Walk-forward 5 (91% of years positive)
- IS 2016-2021: Sharpe 1.12, 1201 nights, avg 5.51 bp, win 59.2%, max DD 21.55%
- OOS 2022-2026: Sharpe 0.97, 900 nights, avg 5.24 bp, win 56.2%, max DD 14.34%, t 2.13
- Stress (1 bar late exit + 2x costs) OOS: Sharpe 0.65.
- COST SENSITIVITY (key risk, ~250 round trips/yr): OOS Sharpe 0.97 at 1.5 bp, 0.70 at 3 bp, 0.32 at 5 bp round trip.
  ESTIMATE of real cost: MNQ ~0.4 bp RT (commission + 1 tick/side); QQQ auctions ~0.2 bp + fees. Edge survives only if fills stay near auction prices.
- Ablation: drop the 200-day filter = H5_overnight: IS 0.83 / OOS 0.41 -> filter roughly doubles OOS edge. Keep it.
- Per year (% notional): {'2016': 3.22, '2017': 13.61, '2018': 4.49, '2019': 12.54, '2020': 21.08, '2021': 11.18, '2022': -6.66, '2023': 6.86, '2024': 26.9, '2025': 17.48, '2026': 2.62}. 2020 21.08% (survived), 2022 -6.66% (LOSS: failed the 2022 check).
- Monte Carlo 1,000 runs OOS: 95th pct max DD 26.48%, worst 47.41%.
- Deflated Sharpe (81 trials): 0.316 (needs 0.95) -> NOT significant.
- Final check: OOS yes | after costs yes | 1 bar late + 2x yes | ablation clean | 2020 yes / 2022 NO | DSR NO.

### WHY THIS COULD FAIL
- Costs: at 5 bp round trip most of the edge is gone; auction fills or MNQ roll/spread costs above estimate kill it.
- 2022-style grinding bear markets that whipsaw around the 200-day average (it lost 6.7% in 2022).
- Overnight gap risk on news (elections, earnings of mega-caps) — exactly what the premium pays for; one large gap can take months of edge.
- Well-known anomaly (overnight drift) -> may be crowded and decaying.

## 2. H6_bigdown_3d — 18/25 — PROVISIONAL (refreshed through 2026-11-04)
- OOS now: Sharpe 0.84, 76 trades, avg 61.38 bp. DSR 0.212 with 81 trials.
- v3 filter tests: none of 5 filters beats plain H6 (uptrend-only 0.61, downtrend-only 0.63, gap-confirm 0.48, first-profit exit 0.35).
- FRAGILITY found: entering at the signal day's close instead of the next open (F4) gives OOS Sharpe -0.01. The edge depends on the
  next-open entry, i.e. on the gap after a down day. Any change to entry timing must be re-tested.
- Earlier detail (v1 write-up, v2 robustness grid) kept below.


---
# Previous versions
# Ranked strategies (Quant v1, 2026-11-03)
Only one hypothesis reached 18/25, and only just. It is NOT statistically proven after deflation; treat as a paper-only probe.

## 1. H6_bigdown_3d — score 18/25 — PROVISIONAL (paper probe only)
- Rules: QQQ daily close-to-close return < -2% -> buy next day at the 09:30 open -> exit at the close of the 3rd trading day (incl. entry day).
  One position at a time. Signal researched on QQQ (no MNQ data yet).
- Thesis: forced de-risking after a big down day overshoots. Who loses: forced/panic sellers.
- Score: Sharpe 3 | Drawdown 5 | Trades 3 | Edge 3 | Walk-forward 4
- IS 2016-2021: Sharpe 0.46, 68 trades, avg 51.5 bp, win 64.7%, max DD 27.13% of notional
- OOS 2022-2026: Sharpe 0.85, 75 trades, avg 62.88 bp, win 54.7%, max DD 9.42%, t-stat 1.79
- Stress (1 bar late + 2x costs), OOS: Sharpe 0.75, avg 54.78 bp -> robust to execution.
- Per year (% of notional): {'2016': 1.13, '2017': 5.99, '2018': -3.57, '2019': 17.62, '2020': 6.31, '2021': 7.53, '2022': 22.43, '2023': 10.63, '2024': 3.85, '2025': -2.71, '2026': 12.97}. 2020 6.31%, 2022 22.43% -> survived both.
- Monte Carlo (1,000 bootstrap runs of OOS active days): 95th pct max DD 29.23%, worst 60.97% of notional.
- Deflated Sharpe (25 trials): probability 0.085 (needs >= 0.95). Benchmark Sharpe for luck alone ~1.47. -> NOT significant.
- Ablation: one rule only (the -2% trigger). Dropping it = buy-and-hold in 3-day blocks, which is a different strategy; no rule to delete.
- Tiered vs flat sizing: NOT TESTABLE yet (one strategy, no historical event calendar, no filter set). Per rules -> flat $100, and Probe $50 for first 2 weeks.
- Final check: OOS yes | after costs yes | 1 bar late + 2x slippage yes | ablation n/a | 2020 & 2022 yes | deflated Sharpe NO.

### WHY THIS COULD FAIL
- Edge is not significant after accounting for 25 trials (DSR 0.085); the 18/25 may be luck.
- Only ~15 trades a year; one bad cluster (e.g. 2008-style crash with many -2% days in a row) is not in the 2016-2026 sample.
- Bootstrap worst-case drawdown (60.97% of notional) is far above the realised 9.42%: falling-knife risk is real.
- 3-day holds go through overnight gaps and events; the backtest did not skip tier-1 events.
- QQQ != MNQ: futures trade overnight; signal and fills will differ slightly.


## Robustness update (Quant v2, 2026-11-04) — H6 parameter neighbourhood
16 nearby settings (trigger x hold days), same engine and costs. Fixed rules, not a search: the live rule stays -2% / 3 days.
| Trigger | Hold days | IS Sharpe | OOS Sharpe | OOS trades |
|---|---|---|---|---|
| -0.015 | 2 | 0.7 | 0.33 | 134 |
| -0.015 | 3 | 0.87 | 0.54 | 115 |
| -0.015 | 4 | 0.68 | 0.44 | 106 |
| -0.015 | 5 | 0.56 | 0.23 | 98 |
| -0.02 | 2 | 0.85 | 0.45 | 84 |
| -0.02 | 3 | 0.46 | 0.85 | 75 |
| -0.02 | 4 | 0.55 | 0.68 | 70 |
| -0.02 | 5 | 0.9 | 0.21 | 62 |
| -0.025 | 2 | 0.7 | -0.05 | 48 |
| -0.025 | 3 | 0.32 | 0.25 | 43 |
| -0.025 | 4 | 0.44 | 0.25 | 41 |
| -0.025 | 5 | 0.65 | -0.0 | 37 |
| -0.03 | 2 | 0.56 | -0.28 | 29 |
| -0.03 | 3 | 0.2 | -0.09 | 27 |
| -0.03 | 4 | 0.27 | 0.23 | 26 |
| -0.03 | 5 | 0.48 | -0.08 | 24 |

What this says:
- The live cell (-2%, 3 days) has the BEST OOS Sharpe of all 16 (0.85). Its neighbours are typically 0.2-0.7 -> the 0.85 is partly luck of the pick.
  Realistic OOS Sharpe to expect: ~0.4-0.5 (ESTIMATE, median of the -1.5% and -2% rows).
- IS Sharpe is positive in all 16 cells; OOS is positive in all 8 cells with triggers of -1.5% or -2%, and fades at -2.5%/-3% (fewer trades, 24-48).
  -> The 'buy after a down day' effect looks real but modest; deeper triggers do not add edge.
- Deflated Sharpe with 61 cumulative trials: 0.287 (needs 0.95) -> still NOT significant.
  (It rose vs v1's 0.085 because the 16 grid cells are highly correlated, which narrows the spread of trial Sharpes; it is not new evidence.)
- Verdict unchanged: PROVISIONAL, paper probe size only. Monitor live paper results against an OOS Sharpe of ~0.45, not 0.85.


## Quant v4 update (2026-11-06) — risk checks on the APPROVED strategies (paper, Probe $50, from Nov 11)
Nothing below changes the approved rules. Two proposals need the owner's OK (questions.md #4).

1. H6 has NO edge after extreme drops. After <= -4% days (23 trades since 2016): IS Sharpe -0.03, OOS -0.30; worst trades in March 2020
   (-11.9%, -6.9%) and Apr 2025 (-5.0%). Excluding drops beyond -5% (R1): OOS Sharpe 0.98 (vs 0.84), stress 0.88, 74 trades, survived 2020/2022.
   CAUTION: this rule was found after seeing the data -> overfitting risk; it is also the classic 'falling knife' rule, which gives it a reason.
   PROPOSAL A: H6 skips signals where the drop is worse than -5%.
2. Vol-scaled sizing beats flat sizing OOS for both (the DESK_RULES test for tiers):
   I3 Sharpe 0.94 -> 1.21, max DD 14.3% -> 8.22%; H6 0.84 -> 0.91, max DD 9.4% -> 6.2%.
   PROPOSAL B: inside the approved Probe cap ($50), scale size DOWN by (normal vol / current vol) when volatility is high; never scale up.
   After Nov 5 the 20-day vol is far above normal, so B would cut size sharply for now.
3. I3 neighbour check: 100-day average OOS 1.05 (lost -8.29% in 2022), 50-day 0.72. The 200-day rule is not a lucky pick.
4. Running I3 + H6 together (R10): OOS Sharpe 1.19, stress 0.91, score 23/25, and positive in BOTH
   2020 (27.39%) and 2022 (15.77%). H6 tends to make money when I3 is switched off (down markets) -> they diversify.
5. Thursday Nov 5 (-6.37%) would have been an H6 'extreme' signal: skipped anyway by the jobs-report blackout. Quant tracks it hypothetically.


## Quant v5 note (2026-11-07) — MULTIPLE-TESTING WARNING
- 10 high-vol regime ideas tested, 0 survivors. Cumulative trials now 121.
- Refreshed (data through 2026-11-06): I3 OOS Sharpe 0.94, H6 0.84 (unchanged edges).
- But deflated-Sharpe probabilities FELL as trials grew: I3 0.32 -> 0.079, H6 -> 0.044 (benchmark 'luck' Sharpe now 1.61).
  Each nightly batch of 10 new ideas raises the bar the approved strategies must clear. The playbook's "10 hypotheses every run" is
  now eroding the evidence for the desk's own strategies. Proposal for the owner: questions.md #5.


## Quant v7 update (2026-11-09)
### Challenger candidate: T2 overnight-after-weak-close — 18/25 — PROVISIONAL
- Rule: if QQQ closes in the bottom 30% of its day range, buy at the close, sell at the next open. Thesis: closing-auction selling overshoots
  and partly reverses overnight; who loses: forced MOC sellers.
- IS Sharpe 0.78 (312 nights), OOS 0.69 (342), stress 0.7; 2022 -1.25% (failed the 2022 check);
  DSR 0.011 with 161 trials -> NOT significant. Exactly at the 18 threshold.
- Overlaps with I3 (both overnight). Not proposed for paper; tracked as challenger in champion.md.
### I3 variant noted, NOT proposed: T1 skip Friday nights — 20/25
- OOS 1.0 vs I3 0.94; IS 1.33 vs 1.12. Small gain, found after 161 trials -> likely partly luck.
  The approved I3 rule stays unchanged.


## Quant v8 note (2026-11-10)
- Second I3 weekday variant: U10 'I3 only Mon-Wed nights' 22/25, OOS 1.09 (IS 1.29), stress 0.75.
  Together with T1 (skip Friday nights, OOS 1.00) this hints Thu/Fri nights add little to I3. But both were found by searching
  (181 cumulative trials) -> NOT proposed. Candidate for a single pre-registered test once paper data exists.
- 0 new survivors. Notable failure: U3 'hold overnight after a +2% day' (OOS -0.45, -12% in 2022).


## (copy) Re-test with hard stops (Quant v9, 2026-11-11) — owner's choice "stops + re-test"
Path: QQQ extended-hours 1-min bars (04:00-20:00 ET); 20:00-04:00 unobserved (gap fills at next price = conservative). 1 MNQ ~= $55,700 (ESTIMATE).
Stops = % of entry sized to today's MNQ: $150=0.27%, $250=0.45%, $300=0.54%. Costs 1.5 bp RT + 1 bp stop slippage; stress = late + 2x costs.
$ columns = per 1 MNQ at today's notional, OOS 2022-2026. Cumulative trials 193.

| Variant | IS Sharpe | OOS Sharpe | OOS stress | Stopped | Avg $/trade | 5th pct $ | Worst $ | 2022 % | Score | DSR |
|---|---|---|---|---|---|---|---|---|---|---|
| I3 stop none | 1.12 | 0.94 | 0.61 | 0.0% | 28.4 | -668.0 | -2988.0 | -6.66 | 21 | 0.058 |
| I3 stop $150 (0.27%) | 0.27 | 0.23 | -0.23 | 52.1% | 5.0 | -253.0 | -1366.0 | -2.81 | 15 | 0.001 |
| I3 stop $250 (0.45%) | 0.22 | -0.06 | -0.51 | 37.3% | -1.6 | -334.0 | -1730.0 | -1.95 | 11 | 0.0 |
| I3 stop $300 (0.54%) | 0.32 | 0.2 | -0.23 | 31.2% | 5.2 | -354.0 | -1730.0 | -2.85 | 15 | 0.001 |
| H6 stop none | 0.57 | 0.79 | 0.7 | 0.0% | 341.9 | -2093.0 | -3336.0 | 22.43 | 18 | 0.017 |
| H6 stop $150 (0.27%) | 0.07 | 0.66 | 0.35 | 87.6% | 173.3 | -164.0 | -204.0 | 13.88 | 16 | 0.001 |
| H6 stop $250 (0.45%) | 0.59 | 0.33 | 0.27 | 82.5% | 88.4 | -265.0 | -265.0 | 7.81 | 12 | 0.0 |
| H6 stop $300 (0.54%) | 0.48 | 0.28 | 0.1 | 81.0% | 76.3 | -315.0 | -337.0 | 8.99 | 11 | 0.0 |

VERDICT: stops FAIL for both.
- I3: any stop cuts OOS Sharpe from 0.94 to <=0.23 and stress goes negative; overnight gaps still blow through stops (worst -$1,366 to -$1,730 per MNQ even WITH a stop).
- H6: stops are hit on 81-88% of trades (a 3-day bounce trade after a -2% day needs room); edge falls to 0.28-0.66 and the $150 version is unstable (IS 0.07).
- Without stops, 1 MNQ does not fit the rules: I3 5th-pct night -$668 and worst -$2,988; H6 5th pct -$2,093, worst -$3,336 (per contract) vs $350/day.
=> Neither approved strategy can be traded at 1 MNQ inside the $350/day limit. MNQ order flow stays BLOCKED pending an owner decision.
