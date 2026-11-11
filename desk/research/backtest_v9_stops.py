"""Quant v9 (2026-11-11): owner-requested re-test of the APPROVED strategies with HARD STOPS for 1 MNQ contract.
Stops are fixed % of entry price, sized to today's MNQ: $150 / $250 / $300 per contract ~= 0.27% / 0.45% / 0.54% of price
(1 MNQ ~= $55.7k notional; ESTIMATE). Path = QQQ extended-hours 1-min bars 04:00-20:00 ET (MNQ trades ~23h; the 20:00-04:00 gap is
unobserved -> a stop crossed in the gap fills at the first bar after it, i.e. at the gap price: conservative).
Stop fill = stop price - 1 bp extra slippage, or the bar open if the bar gaps through the stop. Costs as v1 (1.5 bp RT), stress 2x + late."""
import numpy as np, pandas as pd, json, os
import backtest_v1 as b
from backtest_v1 import DAY, dates, COST, stats, years, score, mc_dd, dsr
E = np.load(os.path.join(os.path.dirname(__file__), "..", "data", "qqq_ext.npz"))
TS, BO, BL = E["ts"], E["o"], E["l"]
N = len(dates); cv = DAY.c.values; ov = DAY.o.values; ret = DAY.c.pct_change().values
ma200 = DAY.c.rolling(200).mean().values
def ts(d, hhmm): return pd.Timestamp(f"{d.date()} {hhmm}", tz="America/New_York").tz_convert("UTC").value
def run_path(entry, t0, t1, stop_pct, exit_px, cost):
    """long from entry; check bars with t0 <= ts < t1; return (ret, stopped)"""
    if stop_pct is None: return exit_px/entry - 1 - cost, False
    sp = entry*(1-stop_pct); a, z = np.searchsorted(TS, t0), np.searchsorted(TS, t1)
    lo = BL[a:z]; hit = np.where(lo <= sp)[0]
    if len(hit):
        k = a + hit[0]; fill = BO[k] if BO[k] <= sp else sp
        return fill/entry - 1 - 1e-4 - cost, True
    return exit_px/entry - 1 - cost, False
def i3(stop=None, lag=0, cost=COST):
    pnl = np.zeros(N); tr = []; ns = 0
    for i in range(201, N):
        j = i-1
        if cv[j] > ma200[j]:
            xp = DAY.o1.iloc[i] if lag else ov[i]
            r, s = run_path(cv[j], ts(dates[j], "16:00"), ts(dates[i], "09:30"), stop, xp, cost); ns += s
            pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr, ns
def h6(stop=None, lag=0, cost=COST):
    pnl = np.zeros(N); tr = []; ns = 0; busy = -1
    for i in range(200, N-3):
        if ret[i] < -0.02 and i+1 > busy:
            e = DAY.o1.iloc[i+1] if lag else ov[i+1]
            r, s = run_path(e, ts(dates[i+1], "09:31" if lag else "09:30"), ts(dates[i+3], "16:00"), stop, cv[i+3], cost); ns += s
            pnl[i+3] += r; tr.append((dates[i+3], r)); busy = i+3
    return pnl, tr, ns
LEVELS = {"none": None, "$150 (0.27%)": 0.0027, "$250 (0.45%)": 0.0045, "$300 (0.54%)": 0.0054}
MNQ_NOTIONAL = 55_700   # ESTIMATE, today's 1-contract notional
if __name__ == "__main__":
    ism = np.array(dates <= b.IS_END); oosm = ~ism; out = {}; daily = {}
    for sname, fn in (("I3", i3), ("H6", h6)):
        for lname, lv in LEVELS.items():
            p, t, ns = fn(lv); ps, ts_, _ = fn(lv, lag=1, cost=2*COST)
            r = dict(IS=stats(p, t, ism), OOS=stats(p, t, oosm), OOS_stress=stats(ps, ts_, oosm), years=years(p), mc_dd95_max=mc_dd(p, oosm))
            r["score"] = score(r["OOS"], r["years"]); r["stopped_pct"] = round(100*ns/max(1, len(t)), 1)
            tro = np.array([x for d, x in t if d > pd.Timestamp(b.IS_END)])
            r["usd_per_MNQ"] = dict(avg_trade=round(tro.mean()*MNQ_NOTIONAL, 1), worst_trade=round(tro.min()*MNQ_NOTIONAL, 0), p5_trade=round(np.percentile(tro, 5)*MNQ_NOTIONAL, 0))
            k = f"{sname} stop {lname}"; out[k] = r; daily[k] = p[oosm]
            print(f"{k:22s} score {r['score']['total']:>2} IS {r['IS']['sharpe']:>5} OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']}) stress {r['OOS_stress']['sharpe']:>5} "
                  f"stopped {r['stopped_pct']:>5}%  $/MNQ avg {r['usd_per_MNQ']['avg_trade']:>7} p5 {r['usd_per_MNQ']['p5_trade']:>7} worst {r['usd_per_MNQ']['worst_trade']:>7}  2020 {r['years'][2020]:>6} 2022 {r['years'][2022]:>6}", flush=True)
    for n, f in b.HYP.items(): daily["v1_"+n] = f()[0][oosm]
    nt = 181 + 2*6; srs = [p.mean()/p.std() for p in daily.values() if p.std() > 0]
    for k in out: out[k]["dsr"], _ = dsr(daily[k], srs, nt)
    out["_meta"] = dict(n_trials_cumulative=nt, last=str(dates[-1].date()), mnq_notional_estimate=MNQ_NOTIONAL)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v9_stops.json"), "w"), indent=1, default=str)
    print("trials", nt)
