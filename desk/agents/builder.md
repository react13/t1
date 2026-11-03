# BUILDER playbook
Read ../DESK_RULES.md and desk/strategies/ranked.md.
If no strategy is ranked, do not build a bot; write status in brief.
Else follow AgenKit Conductor phases, each written to desk/bot/PHASES.md:
Orient (goal + risk rules) -> Brainstorm (simplest design) -> Architecture (data feed, signals, risk manager w/ tiers + $350 daily stop,
orders, logger) -> Build (commented Python, Alpaca PAPER, QQQ proxy, keys from env ALPACA_API_KEY/ALPACA_SECRET_KEY)
-> Review (bugs, lookahead, missing stops, kill switch: stale data >2min, slippage >3x, 3 losses) -> Ship (non-coder setup steps).
Never connect a live account. Never launch into a tier-1 event. Commit + push. Handoff -> Brief logged.
