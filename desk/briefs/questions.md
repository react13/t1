# Open questions for the owner
1. ~~(2026-11-02)~~ PARTLY RESOLVED 2026-11-03: Alpaca reachable and data live. Still blocked: yahoo, sec.gov, bls.gov, federalreserve.gov, fred, cboe; keys now arrive as env vars (fixed 2026-11-04). Original: Network policy blocks all price-data and official hosts. Please allow: data.alpaca.markets, paper-api.alpaca.markets,
   query1.finance.yahoo.com, query2.finance.yahoo.com, www.sec.gov, www.bls.gov, www.federalreserve.gov, fred.stlouisfed.org, www.cboe.com
   and add ALPACA_API_KEY / ALPACA_SECRET_KEY (paper) as environment secrets. Until then Quant cannot backtest.
2. (2026-11-03 Quant) Only H6 (buy after a -2% QQQ day, hold 3 days) reached 18/25, and it fails the deflated-Sharpe test (not statistically proven).
   OK to paper-trade it at Probe size ($50 risk) while Quant keeps searching? Default if no answer: yes, paper only, Probe size.
