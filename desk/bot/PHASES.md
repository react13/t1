# H6 bot — build phases (Builder, 2026-11-03 04:55 ET)

## 1. Orient
- Goal: paper-trade the only ranked strategy, H6_bigdown_3d (desk/strategies/ranked.md), on Alpaca PAPER with QQQ as the MNQ proxy.
- Status of the edge: PROVISIONAL. Score 18/25, deflated-Sharpe probability 0.085 (not significant). Paper probe only.
- Risk rules applied: Probe tier $50 (first 2 weeks); never above flat $100 (tiered sizing unproven); risk = min(tier, $350 - today's realized loss);
  max tier C after 2 losses in a day; $350 daily loss limit; kill switch on stale data >2 min, slippage >3x model, 3 losses in a row;
  no entries on tier-1 blackout dates, holidays, or half-days. Never live.

## 2. Brainstorm (simplest design)
- Once-a-day signal, so no streaming: three short scheduled runs per day instead of a long-running process.
- Use the exchange auctions: market-on-open (OPG) buy, market-on-close (CLS) sell. This matches the backtest's 09:30 open / close prices.
- Whole shares only (OPG/CLS orders don't take fractional quantities).

## 3. Architecture
| Part | How |
|---|---|
| Data feed | Signal: SIP 15:59 1-min bar closes of the last two full sessions (older than 15 min, allowed on free plan). Freshness: IEX latest trade. |
| Calendar | Alpaca /v2/calendar: skip holidays and early closes; exit day counted in full sessions. |
| Signal | close-to-close < -2% -> buy at today's open; exit at close of 3rd full session. One position at a time. |
| Risk manager | risk_budget(): tiers + $350 daily stop. Size = floor(risk / (price x 3.51%)), 3.51% = 5th-percentile 3-day loss in backtest. |
| Kill switch | guard run every 5 min: stale IEX data >120 s, or realized + open loss <= -$350 -> flatten + halt. 3 losses in a row / slippage >3x model -> halt. |
| Orders | POST /v2/orders to paper-api only (URL hard-coded). Idempotent client_order_id per day. |
| Logger | trades.csv (orders, fills, slippage, P&L) + state.json (position, streaks, halt). |

## 4. Build
- desk/bot/h6_bot.py (commented), desk/bot/blackout.txt. Keys from env ALPACA_API_KEY / ALPACA_SECRET_KEY (fallback ~/.config/alpaca.env).
- Default DRY RUN; `--paper` is required to send paper orders. `--asof=YYYY-MM-DD` replays a past morning (always dry).

## 5. Review
- Parity test: replayed mornings 2026-10-19, 10-23, 10-26, 11-02. Closes match the backtest exactly (715.33 -> 690.53 = -3.47%);
  signals fire on the same days as the backtest; 11-02 correctly SKIPPED (election blackout). 2 shares at ~$705 = Probe $50 / 3.51%.
- Bug found and fixed: close fetch returned the 16:00 bar instead of 15:59 (0.08% price mismatch vs backtest).
- Bug found and fixed: slippage check compared the fill with the prior close (that is the gap, not slippage). Now compares with the
  09:30 open / 15:59 close model prices.
- Bug found and fixed: exit could land on a half-day after the 13:00 close. Exit now counts full sessions only.
- Lookahead: signal uses only closes of finished sessions; entry is the next open. None found.
- Missing stops: H6 was backtested WITHOUT a stop. The bot adds only the $350 daily-loss flatten (a rule, not a strategy change).
  Worst backtest trade was -11.9%; at 2 shares that is about -$170.
- Known limits: stale-data halt stays on until the owner clears `halted` in state.json (conservative); blackout dates are maintained by
  hand from EVENTS.md (NFP/CPI dates UNVERIFIED); container reset loses ~/.config/alpaca.env (keys) -> runs fail closed.
- Not yet tested with real paper orders: OPG/CLS acceptance, fill reconciliation. First paper week = test week.

## 6. Ship (setup for a non-coder)
1. Nothing runs yet. The bot needs your OK (desk/briefs/questions.md #2) before it sends even paper orders.
2. Once you say yes, Builder adds three scheduled runs (weekdays ET): 09:20 `morning --paper`, every 5 min 09:35-15:45 `guard --paper`,
   15:40 `close --paper`. Each run commits state.json and trades.csv.
3. To check it: `python3 desk/bot/h6_bot.py status`. To stop it: set `"halted": "owner stop"` in desk/bot/state.json, or tell the desk "stop the bot".
4. Earliest possible entry: the first H6 signal on a non-blackout day (after 2026-11-10 at the current blackout list).

## Builder run 2 — 2026-11-04 04:53 ET
- Ranked list unchanged (H6 only, still PROVISIONAL). No code change needed.
- Keys now come from environment variables (fixed by owner); bot authenticates without the fallback file.
- Dry-run checks: status OK (paper ACTIVE, $100k, no positions); today's signal check 11-02 681.13 -> 11-03 685.34 = +0.62% -> no signal;
  10-19 replay still matches the backtest (2 shares OPG).
- Monitoring benchmark updated from Quant v2: judge live paper results against an OOS Sharpe of ~0.45 (neighbourhood median), not 0.85.
  With ~15 trades a year, no meaningful verdict before ~30 trades (ESTIMATE: about 2 years). Weekly review should track hit rate and average
  trade against the backtest (OOS win 54.7%, avg +0.63% per trade) instead of P&L alone.
- Still waiting on owner OK (questions.md #2). Nothing scheduled; nothing sent.

# I3 overnight-uptrend bot — phases (Builder run 3, 2026-11-05 04:55 ET)
1. Orient: ranked #1 I3_overnight_uptrend (21/25, PROVISIONAL, DSR 0.32). Same risk rules as H6; Probe $50 in first 2 weeks; never above $100.
2. Brainstorm: one decision a day at 15:45; exchange auctions both ways (MOC buy, MOO sell) to match backtest prices and keep costs at
   auction level (cost sensitivity is this strategy's main risk).
3. Architecture: shares h6_bot.py plumbing (calendar, kill switch, tiers, logging, PAPER-only URL). State in state_i3.json, log trades_i3.csv.
   Filter = 15:45 price vs 200-day average of the last 199 full-session SIP daily closes + the 15:45 price.
   Size = floor(risk / (price x 1.11%)), 1.11% = 5th-pct overnight loss with filter on. Probe $50 -> ~6 shares (~$4,100).
4. Build: desk/bot/i3_bot.py (evening / morning / status). DRY RUN default.
5. Review:
   - Lookahead found and fixed BEFORE build: backtest used the close for the filter, but MOC orders must go in by ~15:50. Re-tested with the
     15:45 price: OOS Sharpe 1.02 (vs 0.97), stress 0.69, same 900 nights -> deciding at 15:45 is fine.
   - Parity: replayed 10-27, 10-30 (filter ON, 6 shares) and 2025-04-07 (OFF). Bot 200-day avg 678.37 vs backtest 678.32 on 10-30
     (0.007% gap: bot uses official daily closes, backtest uses the 15:59 bar). Acceptable.
   - Blackout: bot skips NEW overnight positions on blackout dates (stricter than backtest; costs a few nights a month).
   - Worst backtest overnight gap -7.0% -> ~-$290 at 6 shares, inside the $350 daily limit but close to it.
   - NOT DONE: fill reconciliation and loss-streak update for I3 (needs real fills) -> must be added in the first paper week before
     the 3-losses kill switch can work for I3. Stated plainly so nobody assumes it works.
6. Ship: not scheduled. Needs owner OK (questions.md #3). If approved: weekdays 15:42 `evening --paper`, 09:20 `morning --paper`.
