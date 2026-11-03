# Setup status (for any new session picking up the desk)
- Alpaca hosts allowed: YES (paper-api / data.alpaca.markets reachable).
- Keys: owner set ALPACA_API_KEY / ALPACA_SECRET_KEY as environment variables; not visible in session started before the change.
- Still blocked (optional): yahoo, sec.gov, bls.gov, federalreserve.gov, fred, cboe -> events marked UNVERIFIED.
- Scheduled tasks (bound to session_01Cc726jzT2ydA2BrfkEebCm; move them to the new session):
  Scout trig_01DD16k6EYNzbuav1nnq5DQF | Quant trig_011d7VmD52mM77gZbC9KiZ2g | Builder trig_01BSZfayqAZBeXo7brHNaL7W
  Brief trig_01A3E8oRoA21WVUEcGdpdYWN | Weekly trig_01N8111kr9761xYWsWZ6o2yk
- Next: verify account read-only, pull QQQ 1-min bars 2016->today, run Quant playbook.
