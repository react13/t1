"""Quant v4 (2026-11-06): 10 pre-registered risk/robustness variants of the two APPROVED paper strategies (I3, H6).
Motivation: Nov 5 QQQ -6.37% (4th worst day since 2016). Question: how do the strategies behave around extreme days,
and does vol-scaled sizing beat flat sizing (DESK_RULES: tiers must beat flat OOS)? Same engine/costs as v1."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import DAY, dates, COST, swing, stats, years, score, mc_dd, dsr
N = len(dates); cv = DAY.c.values; ov = DAY.o.values; ret = DAY.c.pct_change().values
rv20 = DAY.c.pct_change().rolling(20).std().shift(0).values          # known at close i
ma = {n: DAY.c.rolling(n).mean().values for n in (50, 100, 200)}
med_rv = np.nanmedian(rv20[:np.searchsorted(dates, np.datetime64(b.IS_END))])   # IS median only (no lookahead into OOS)

def overnight(cond, w=lambda i: 1.0, lag=0, cost=COST):
    pnl = np.zeros(N); tr = []
    for i in range(201, N):
        j = i - 1
        if cond(j):
            xp = DAY.o1.iloc[i] if lag else ov[i]; r = w(j) * (xp / cv[j] - 1 - cost); pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr
def h6(cond=lambda i: True, w=lambda i: 1.0, lag=0, cost=COST):
    e = [(i+1, i+3, 1, "c") for i in range(200, N-3) if ret[i] < -0.02 and cond(i)]
    p, t = swing(e, cost, lag)
    if w is None: return p, t
    # apply per-trade weight to the daily pnl of each trade window
    pw = np.zeros(N); tw = []
    for (i, j, s, f) in e:
        pass
    return p, t
def h6_weighted(wfn, lag=0, cost=COST):
    pnl = np.zeros(N); tr = []; busy = -1
    for i in range(200, N-3):
        if ret[i] < -0.02 and i+1 > busy:
            wt = wfn(i); p, t = swing([(i+1, i+3, 1, "c")], cost, lag)
            pnl += wt * p; tr += [(d, wt*r) for d, r in t]; busy = i+3
    return pnl, tr

I3 = lambda j: cv[j] > ma[200][j]
VARS = {
 "R1_h6_moderate_drops":  lambda lag=0, cost=COST: h6(lambda i: ret[i] > -0.05, lag=lag, cost=cost),
 "R2_h6_extreme_drops":   lambda lag=0, cost=COST: h6(lambda i: ret[i] <= -0.04, lag=lag, cost=cost),
 "R3_h6_volscaled":       lambda lag=0, cost=COST: h6_weighted(lambda i: min(2.0, med_rv / rv20[i]), lag, cost),
 "R4_i3_skip_highvol":    lambda lag=0, cost=COST: overnight(lambda j: I3(j) and rv20[j] <= 2*med_rv, lag=lag, cost=cost),
 "R5_i3_volscaled":       lambda lag=0, cost=COST: overnight(I3, w=lambda j: min(2.0, med_rv / rv20[j]), lag=lag, cost=cost),
 "R6_i3_skip_after_-3pct":lambda lag=0, cost=COST: overnight(lambda j: I3(j) and ret[j] > -0.03, lag=lag, cost=cost),
 "R7_h6_no_cluster":      lambda lag=0, cost=COST: h6(lambda i: not any(ret[i-5:i] < -0.02), lag=lag, cost=cost),
 "R8_i3_ma100":           lambda lag=0, cost=COST: overnight(lambda j: cv[j] > ma[100][j], lag=lag, cost=cost),
 "R9_i3_ma50":            lambda lag=0, cost=COST: overnight(lambda j: cv[j] > ma[50][j], lag=lag, cost=cost),
 "R10_combo_i3_h6":       lambda lag=0, cost=COST: tuple(map(lambda x: x, (
                              overnight(I3, lag=lag, cost=cost)[0] + h6(lag=lag, cost=cost)[0],
                              overnight(I3, lag=lag, cost=cost)[1] + h6(lag=lag, cost=cost)[1]))),
}
if __name__ == "__main__":
    ism = np.array(dates <= b.IS_END); oosm = ~ism; out = {}; daily = {}
    base = {"I3": overnight(I3), "H6": h6()}
    for k, (p, t) in base.items():
        out["_base_"+k] = dict(IS=stats(p, t, ism), OOS=stats(p, t, oosm), years=years(p))
    for name, fn in VARS.items():
        p, t = fn(); ps, ts = fn(lag=1, cost=2*COST)
        r = dict(IS=stats(p, t, ism), OOS=stats(p, t, oosm), OOS_stress=stats(ps, ts, oosm), years=years(p), mc_dd95_max=mc_dd(p, oosm))
        r["score"] = score(r["OOS"], r["years"]); out[name] = r; daily[name] = p[oosm]
        print(f"{name:24s} score {r['score']['total']:>2}  IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4})  OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4})  stress {r['OOS_stress']['sharpe']:>5}  DD {r['OOS']['maxdd']:>5}  2020 {r['years'][2020]:>6}  2022 {r['years'][2022]:>6}", flush=True)
    for k in out:
        if k.startswith("_base"): print(k, "IS", out[k]["IS"]["sharpe"], "OOS", out[k]["OOS"]["sharpe"], "DD", out[k]["OOS"]["maxdd"])
    # H6 behaviour after extreme days: list every H6 trade whose signal day was <= -4%
    ext = [(str(dates[i].date()), round(ret[i]*100, 2), round((cv[i+3]/ov[i+1]-1)*100, 2)) for i in range(200, N-3) if ret[i] <= -0.04]
    out["_h6_extreme_signal_trades"] = ext; print("H6 trades after <= -4% days (signal date, drop %, 3-day trade %):", ext)
    for name, fn in b.HYP.items(): daily["v1_"+name] = fn()[0][oosm]
    n_trials = 81 + 2*len(VARS)
    srs = [p.mean()/p.std() for p in daily.values() if p.std() > 0]
    for name in VARS: out[name]["dsr"], _ = dsr(daily[name], srs, n_trials)
    out["_meta"] = dict(n_trials_cumulative=n_trials, sessions=N, last=str(dates[-1].date()), med_rv20_IS=round(float(med_rv)*100, 3))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v4.json"), "w"), indent=1, default=str)
    print("trials", n_trials, "IS median 20d vol %", out["_meta"]["med_rv20_IS"])
