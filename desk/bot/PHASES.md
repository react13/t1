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
