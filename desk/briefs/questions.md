# Open questions for the owner
1. ~~(2026-11-02)~~ PARTLY RESOLVED 2026-11-03: Alpaca reachable and data live. Still blocked: yahoo, sec.gov, bls.gov, federalreserve.gov, fred, cboe; keys not yet arriving as env vars. Original: Network policy blocks all price-data and official hosts. Please allow: data.alpaca.markets, paper-api.alpaca.markets,
   query1.finance.yahoo.com, query2.finance.yahoo.com, www.sec.gov, www.bls.gov, www.federalreserve.gov, fred.stlouisfed.org, www.cboe.com
   and add ALPACA_API_KEY / ALPACA_SECRET_KEY (paper) as environment secrets. Until then Quant cannot backtest.
