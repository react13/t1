# Open questions for the owner
1. ~~(2026-11-02)~~ PARTLY RESOLVED 2026-11-03: Alpaca reachable and data live. Still blocked: yahoo, sec.gov, bls.gov, federalreserve.gov, fred, cboe; keys now arrive as env vars (fixed 2026-11-04). Original: Network policy blocks all price-data and official hosts. Please allow: data.alpaca.markets, paper-api.alpaca.markets,
   query1.finance.yahoo.com, query2.finance.yahoo.com, www.sec.gov, www.bls.gov, www.federalreserve.gov, fred.stlouisfed.org, www.cboe.com
   and add ALPACA_API_KEY / ALPACA_SECRET_KEY (paper) as environment secrets. Until then Quant cannot backtest.
2. RESOLVED 2026-11-06: owner approved paper Probe from Nov 11 (see decisions.md). Original: (2026-11-03 Quant) Only H6 (buy after a -2% QQQ day, hold 3 days) reached 18/25, and it fails the deflated-Sharpe test (not statistically proven).
   OK to paper-trade it at Probe size ($50 risk) while Quant keeps searching? No answer = bot stays DRY-RUN (explicit owner OK required).
3. RESOLVED 2026-11-06: owner approved paper Probe from Nov 11 (see decisions.md). Original: (2026-11-05 Quant) New provisional #1: I3 (hold QQQ overnight only when above its 200-day average), 21/25 but not statistically proven
   and very cost-sensitive. Should Builder add it to the dry-run bot alongside H6? Nothing trades without your explicit OK.
4. (2026-11-06 Quant) Two optional safety changes to the APPROVED paper strategies (details: desk/strategies/ranked.md, Quant v4):
   A) H6 skips signals after drops worse than -5% (no edge after extreme days; found after seeing data, so overfitting risk).
   B) Within the $50 Probe cap, size DOWN when volatility is high (never up). Better Sharpe and lower drawdown OOS for both.
   Reply "A", "B", "both" or "neither". Default without a reply: approved rules stay exactly as they are.
5. (2026-11-07 Quant) Process change: testing 10 new ideas EVERY night (121 trial versions so far) keeps lowering the statistical
   confidence in the approved strategies (deflated-Sharpe I3 0.32 -> 0.08). Proposal: Quant tests new ideas ONCE A WEEK (Sunday, max 10),
   and on other nights only monitors the paper bots vs their backtest. Reply "weekly" or "keep nightly". Default: keep the current playbook.
6. (2026-11-11 Quant) MNQ re-test with stops FAILED (details: desk/briefs/mnq_migration.md). At 1 MNQ neither strategy fits $350/day.
   Options: (a) keep paper trading QQQ on Alpaca as approved (correct size, no change) and report it in MNQ terms;
   (b) MNQ on the NinjaTrader demo WITHOUT stops, with limits raised to fit 1 contract (I3 worst ~-$3,000/night; H6 worst ~-$3,300);
   (c) I3 only on MNQ without stops, limits raised for I3 only. Reply "a", "b" or "c". Default: (a).
