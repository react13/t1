"""Quant v3 (2026-11-05): 5 pre-registered H6 filters + 5 new independent ideas. Same engine/costs/scoring as v1.
Cumulative trials: v1 25 + v2 46 (10 bases, 10 stress, 16 grid... counted 36 new) -> 61, plus this run."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import O, H, L, C, pc, DAY, dates, COST, intraday, swing, stats, years, score, mc_dd, dsr
N = len(dates); cv = DAY.c.values; ov = DAY.o.values; ret = DAY.c.pct_change().values
ma200 = DAY.c.rolling(200).mean().values; hv, lv = DAY.h.values, DAY.l.values

def h6_entries(cond):
    return [(i+1, i+3, 1, "c") for i in range(200, N-3) if ret[i] < -0.02 and cond(i)]
def F1_h6_uptrend(lag=0, cost=COST, **k):   return swing(h6_entries(lambda i: cv[i] > ma200[i]), cost, lag)
def F2_h6_downtrend(lag=0, cost=COST, **k): return swing(h6_entries(lambda i: cv[i] <= ma200[i]), cost, lag)
def F3_h6_gapdown_confirm(lag=0, cost=COST, **k):   # needs next open below signal close (known at the open)
    return swing(h6_entries(lambda i: ov[i+1] < cv[i]), cost, lag)
def F4_h6_moc_entry(lag=0, cost=COST, **k):          # signal from 15:50 price, enter at that day's close, hold 3 more sessions
    pnl = np.zeros(N); tr = []; busy = -1
    for i in range(200, N-3):
        if i <= busy: continue
        k_ = 380 + (1 if lag else 0)
        if C[i,380] / pc[i] - 1 < -0.02:
            ep = C[i, 389] if not lag else C[i, 389]   # MOC fill = close either way; lag shifts signal bar
            if lag and C[i, k_] / pc[i] - 1 >= -0.02: continue
            prev = ep
            for d in range(i+1, i+4): pnl[d] += (cv[d] - prev) / ep; prev = cv[d]
            pnl[i+1] -= cost; tr.append((dates[i+3], prev/ep - 1 - cost)); busy = i+3
    return pnl, tr
def F5_h6_first_profit_exit(lag=0, cost=COST, **k):  # exit at first close above entry, max 3 days
    e = []
    for i in range(200, N-3):
        if ret[i] < -0.02:
            ep = ov[i+1]; j = i+1
            while j < i+3 and cv[j] <= ep: j += 1
            e.append((i+1, j, 1, "c"))
    return swing(e, cost, lag)
def I1_month_last_day(lag=0, cost=COST, **k):
    def f(i): return [(1, 0, 389, None)] if i+1 < N and dates[i].month != dates[i+1].month else []
    return intraday(f, lag, cost)
def I2_morning_flush_reversal(lag=0, cost=COST, **k):   # down > 1.5% vs prior close by 11:00 -> long 11:00 -> close
    def f(i): return [(1, 90, 389, None)] if C[i,89] / pc[i] - 1 < -0.015 else []
    return intraday(f, lag, cost)
def I3_overnight_uptrend(lag=0, cost=COST, **k):        # overnight hold only when close > 200dma
    pnl = np.zeros(N); tr = []
    for i in range(201, N):
        if cv[i-1] > ma200[i-1]:
            xp = DAY.o1.iloc[i] if lag else ov[i]; r = xp / cv[i-1] - 1 - cost; pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr
def I4_turnaround_tuesday(lag=0, cost=COST, **k):       # down Monday -> long Tuesday open->close
    def f(i): return [(1, 0, 389, None)] if dates[i].weekday() == 1 and dates[i-1].weekday() == 0 and ret[i-1] < 0 else []
    return intraday(f, lag, cost)
def I5_inside_day_breakout(lag=0, cost=COST, **k):      # yesterday inside day -> trade first break of yesterday's H/L, stop other side
    def f(i):
        if i < 2 or not (hv[i-1] <= hv[i-2] and lv[i-1] >= lv[i-2]): return []
        up = np.where(H[i] > hv[i-1])[0]; dn = np.where(L[i] < lv[i-1])[0]
        if not len(up) and not len(dn): return []
        if len(up) and (not len(dn) or up[0] < dn[0]):
            return [(1, min(up[0]+1, 389), 389, lv[i-1])] if up[0] < 389 else []
        return [(-1, min(dn[0]+1, 389), 389, hv[i-1])] if dn[0] < 389 else []
    return intraday(f, lag, cost)

HYP = {k: v for k, v in globals().items() if k[:2] in ("F1","F2","F3","F4","F5","I1","I2","I3","I4","I5") and callable(v)}
if __name__ == "__main__":
    ism = np.array(dates <= b.IS_END); oosm = ~ism; out = {}; daily = {}
    for name, fn in HYP.items():
        base = fn(); st = fn(lag=1, cost=2*COST)
        r = dict(IS=stats(*base, ism), OOS=stats(*base, oosm), OOS_stress=stats(*st, oosm), years=years(base[0]), mc_dd95_max=mc_dd(base[0], oosm))
        r["score"] = score(r["OOS"], r["years"]); out[name] = r; daily[name] = base[0][oosm]
        print(name, r["score"]["total"], "IS", r["IS"]["sharpe"], r["IS"]["trades"], "OOS", r["OOS"]["sharpe"], r["OOS"]["trades"], "stress", r["OOS_stress"]["sharpe"], "y2020", r["years"][2020], "y2022", r["years"][2022], flush=True)
    for name, fn in b.HYP.items(): daily["v1_" + name] = fn()[0][oosm]
    for t in (-0.015, -0.02, -0.025, -0.03):
        for h in (2, 3, 4, 5): daily[f"g{t}{h}"] = b.H6_bigdown(thr=t, hold=h)[0][oosm]
    n_trials = 61 + 2*len(HYP)
    srs = [p.mean()/p.std() for p in daily.values() if p.std() > 0]
    for name in out: out[name]["dsr"], out[name]["sr0_ann"] = dsr(daily[name], srs, n_trials)
    h6 = b.H6_bigdown()[0]
    out["_H6_refresh"] = dict(OOS=stats(*b.H6_bigdown(), oosm), dsr=dsr(h6[oosm], srs, n_trials))
    out["_meta"] = dict(n_trials_cumulative=n_trials, sessions=N, last=str(dates[-1].date()))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v3.json"), "w"), indent=1, default=str)
    print("H6 refreshed", out["_H6_refresh"], "trials", n_trials)
