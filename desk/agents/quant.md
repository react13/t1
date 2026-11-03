# QUANT playbook
Read ../DESK_RULES.md and the last 24h of desk/findings/.
1. Check data access (python fetch of QQQ/NQ history). If no real price data is reachable: DO NOT backtest, DO NOT estimate results.
   Write hypotheses only, mark status BLOCKED-NO-DATA, and leave one question in desk/briefs/questions.md.
2. Write >= 10 hypotheses (desk/strategies/hypotheses_YYYY-MM-DD.md): thesis, reason, who loses, rules, intraday or swing.
3. Backtest each: IS 2016-2021, OOS 2022-today, walk-forward; costs per rules; rerun 1 bar late + 2x slippage.
4. Score 5 criteria (1-5); ablation per rule; 1,000-run Monte Carlo worst DD; deflated Sharpe for N trials. Test tiered vs flat sizing.
5. Survivors >= 18 -> desk/strategies/ranked.md. Kills -> desk/graveyard/ with reason. Code in desk/research/.
6. Handoff -> Builder logged. Commit + push.
