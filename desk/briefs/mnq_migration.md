# Moving the paper probe from QQQ to real MNQ futures (paper) — 2026-11-11
Owner request (in session, 2026-11-11): "i want qqq converted to mnq futures contracts" -> chose "Trade real MNQ (paper)".
Nothing is changed yet. QQQ paper probe continues exactly as approved until the owner picks a broker and a risk change.

## Size of one contract (ESTIMATE; NQ 28,060 Mon 18:58 ET via Investing.com / QQQ 679.35)
- NQ/QQQ ~41.3 -> NQ ~27,870 -> 1 MNQ = $2 x NQ = ~$55,700 notional = ~83 QQQ shares. QQQ $1 = ~41 NQ pts = ~$83 per MNQ.
- Today's approved sizes are 0.07 MNQ (I3, 6 sh) and 0.02 MNQ (H6, 2 sh). MNQ cannot be traded in fractions; the minimum is 1.

## Risk with 1 MNQ vs DESK_RULES (tiers $50-$300, $350/day, $10k capital)
| Strategy | Typical bad outcome (5th pct) | Worst backtest | vs rules |
|---|---|---|---|
| I3 overnight | -$619 | -$3,902 | breaks $300 tier and $350/day |
| H6 3-day | -$1,957 | -$6,622 | breaks everything; ~66% of $10k capital at worst |

## Broker paper options (secondary sources, to verify)
- Tradovate (NinjaTrader): demo REST API exists (demo.tradovateapi.com). API access reportedly needs a LIVE account with >$1,000 and an API add-on (~$25/mo).
- Interactive Brokers: paper futures supported, but retail Web API needs the Client Portal Gateway (a local Java process) -> needs a machine that stays on; may not run in this cloud desk.
Both need: an account in the owner's name, keys stored as environment secrets, and the broker host allowed in network settings.

## Risk choices (owner decision)
A) Raise limits to fit 1 MNQ (e.g. I3 risk ~$650, daily limit > $650). H6 does not fit any sane limit at 1 MNQ.
B) Keep the $350/day limit and add hard stops (MNQ trades ~23h, so overnight stops are possible, unlike QQQ). Stops change the strategy -> Quant must re-test first (needs NQ overnight data).
C) Run I3 only on MNQ (closest fit), drop H6 from the futures account.

## Update 2026-11-11 ~00:45 ET — owner has a NinjaTrader account with a demo (sim) account
- Broker: NinjaTrader Trade API (Tradovate platform). Demo host demo.tradovateapi.com; market data md-demo.tradovateapi.com.
  Hosts added to the environment allowlist (approved by owner); demo endpoint reachable (HTTP 400 on an empty auth request = alive).
- Auth (docs.ninjatrader.com/api/authentication): POST /v1/auth/accesstokenrequest with name, password, appId, appVersion, cid, sec,
  deviceId -> Bearer token (~90 min, renewable). cid/sec are "issued by NinjaTrader"; the docs do not say how an individual gets them
  (expected: NinjaTrader web platform account settings -> API access, possibly a paid add-on / live account requirement; VERIFY).
- Owner to add as ENVIRONMENT VARIABLES (never in chat): NT_USERNAME, NT_PASSWORD, NT_CID, NT_SEC.
- Still open: risk choice (stops + re-test / I3 only / raise limits). No MNQ order before that choice and a Builder Review.


## Re-test with hard stops (Quant v9, 2026-11-11) — owner's choice "stops + re-test"
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


## Quant v10 (2026-11-11): 10 intraday ideas sized for 1 MNQ ($300 stop) — 0 survivors (best 17/25, unstable). No MNQ-sized edge found yet.
