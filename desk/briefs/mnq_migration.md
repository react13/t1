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
