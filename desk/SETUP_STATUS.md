# Setup status (for any session picking up the desk)
Updated 2026-11-03 01:50 UTC.
- Alpaca: WORKING. Paper account ACTIVE, $100k equity, read-only check only (no orders).
- Keys: NOT in environment variables yet. This session keeps them in ~/.config/alpaca.env (chmod 600, outside the repo).
  If that file is missing (container reset), mark Alpaca steps BLOCKED and ask the owner to fix the env vars.
- Data: desk/tools/fetch_bars.py SYMBOL START -> desk/data/SYMBOL_1min.csv.gz (gitignored). SIP feed, split-adjusted, QQQ from 2016-01-04.
- Still blocked (optional): yahoo, sec.gov, bls.gov, federalreserve.gov, fred, cboe -> events marked UNVERIFIED.
- Scheduled tasks now bound to session_01Cc726iUbevPrqzt1G2RXAi:
  Scout trig_0121DwGkqLijbhL83TQbSp7P | Quant trig_01D3GMXwP4vT74tBgwaxTxB5 | Builder trig_013eTYJ2XqL3y54cn4i3adRx
  Brief trig_01KC6W8VsZZCtUuEMRkAfk1k | Weekly trig_01PPRJnzaxje6KjiGQvgi2mh
  Old copies on session_01Cc726jzT2ydA2BrfkEebCm are disabled (not deleted).
- Alpaca free plan: SIP data newer than 15 min is refused. Use feed=iex for latest/snapshots; SIP for history.
- cnbc.com is blocked by network policy too (optional).
