"""Quant v5 (2026-11-07): 10 pre-registered HIGH-VOL REGIME hypotheses (the market is now -9.6% in 2 weeks, below the 200-day avg).
Same engine/costs/scoring as v1. Rules fixed before running."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import O, C, pc, DAY, dates, COST, intraday, swing, stats, years, score, mc_dd, dsr
N = len(dates); cv = DAY.c.values; ov = DAY.o.values; ret = DAY.c.pct_change().values
rv = DAY.c.pct_change().rolling(20).std().values
med = np.nanmedian(rv[:np.searchsorted(dates, np.datetime64(b.IS_END))]); HV = lambda i: rv[i] > 1.5*med
ma200 = DAY.c.rolling(200).mean().values; below = cv < ma200

def overnight(cond, side=1, lag=0, cost=COST):
    pnl = np.zeros(N); tr = []
    for i in range(201, N):
        j = i-1
        if cond(j):
            xp = DAY.o1.iloc[i] if lag else ov[i]; r = side*(xp/cv[j]-1) - cost; pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr
def P1(lag=0, cost=COST, **k):   # follow-through: day after a +1% bounce that followed a <=-4% day -> long open->close
    return intraday(lambda i: [(1,0,389,None)] if i>2 and ret[i-1]>0.01 and ret[i-2]<=-0.04 else [], lag, cost)
def P2(lag=0, cost=COST, **k):   # fade the first up day after a <=-4% day -> short next open->close
    return intraday(lambda i: [(-1,0,389,None)] if i>2 and ret[i-1]>0 and ret[i-2]<=-0.04 else [], lag, cost)
def P3(lag=0, cost=COST, **k):   # weekly reversal: week < -4% -> buy Monday open, sell Friday close
    e=[]
    for i in range(5, N-5):
        if dates[i].weekday()==4 and cv[i]/cv[i-5]-1 < -0.04:
            j=i+1; k_=j
            while k_+1<N and dates[k_+1].weekday()>dates[k_].weekday(): k_+=1
            e.append((j,k_,1,"c"))
    return swing(e, cost, lag)
def P4(lag=0, cost=COST, **k):   # short overnight when below 200-day AND high vol (mirror of I3)
    return overnight(lambda j: below[j] and HV(j), side=-1, lag=lag, cost=cost)
def P5(lag=0, cost=COST, **k):   # high vol gap-down > 1% -> buy open, sell close
    return intraday(lambda i: [(1,0,389,None)] if HV(i-1) and O[i,0]/pc[i]-1 < -0.01 else [], lag, cost)
def P6(lag=0, cost=COST, **k):   # high vol gap-up > 1% -> fade open->close
    return intraday(lambda i: [(-1,0,389,None)] if HV(i-1) and O[i,0]/pc[i]-1 > 0.01 else [], lag, cost)
def P7(lag=0, cost=COST, **k):   # first close below 200-day in 50 sessions -> short 5 days
    e=[(i+1,i+5,-1,"c") for i in range(250,N-5) if below[i] and not below[i-50:i].any()]
    return swing(e, cost, lag)
def P8(lag=0, cost=COST, **k):   # close crosses back above 200-day after >= 10 sessions below -> long 5 days
    e=[(i+1,i+5,1,"c") for i in range(250,N-5) if not below[i] and below[i-10:i].all()]
    return swing(e, cost, lag)
def P9(lag=0, cost=COST, **k):   # high vol: short Fri close -> Mon open (weekend risk aversion)
    pnl=np.zeros(N); tr=[]
    for i in range(201,N):
        if dates[i].weekday()==0 and dates[i-1].weekday()==4 and HV(i-1):
            xp = DAY.o1.iloc[i] if lag else ov[i]; r=-(xp/cv[i-1]-1)-cost; pnl[i]=r; tr.append((dates[i],r))
    return pnl,tr
def P10(lag=0, cost=COST, **k):  # late-day momentum (H11) only when vol is NOT high
    return intraday(lambda i: [(np.sign(C[i,269]/pc[i]-1),270,389,None)] if not HV(i-1) and abs(C[i,269]/pc[i]-1)>0.01 else [], lag, cost)
DESC = {"P1":"Follow-through: day after a +1% bounce that followed a <=-4% day, long open->close","P2":"Fade the first up day after a <=-4% day (short next open->close)",
"P3":"Weekly reversal: week < -4% -> long Mon open to Fri close","P4":"Short overnight when below 200-day avg AND 20-day vol > 1.5x normal",
"P5":"High vol + gap-down >1% -> long open->close","P6":"High vol + gap-up >1% -> short open->close","P7":"First close below 200-day in 50 sessions -> short 5 days",
"P8":"Close back above 200-day after 10+ sessions below -> long 5 days","P9":"High vol: short Fri close -> Mon open","P10":"Late-day momentum (H11) only when vol is not high"}
HYP = {k: globals()[k] for k in DESC}
if __name__ == "__main__":
    ism = np.array(dates <= b.IS_END); oosm = ~ism; out = {}; daily = {}
    for name, fn in HYP.items():
        p,t = fn(); ps,ts = fn(lag=1, cost=2*COST)
        r = dict(IS=stats(p,t,ism), OOS=stats(p,t,oosm), OOS_stress=stats(ps,ts,oosm), years=years(p), mc_dd95_max=mc_dd(p,oosm))
        r["score"] = score(r["OOS"], r["years"]); out[name] = r; daily[name] = p[oosm]
        print(f"{name:4s} score {r['score']['total']:>2}  IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4})  OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4})  stress {r['OOS_stress']['sharpe']:>5}  2020 {r['years'][2020]:>6}  2022 {r['years'][2022]:>6}  {DESC[name]}", flush=True)
    for n,f in b.HYP.items(): daily["v1_"+n] = f()[0][oosm]
    n_trials = 101 + 2*len(HYP); srs = [p.mean()/p.std() for p in daily.values() if p.std()>0]
    for n in out: out[n]["dsr"], _ = dsr(daily[n], srs, n_trials)
    i3 = __import__("backtest_v4").overnight(lambda j: cv[j] > ma200[j]); h6 = b.H6_bigdown()
    out["_refresh"] = dict(I3_OOS=stats(*i3, oosm), H6_OOS=stats(*h6, oosm), I3_dsr=dsr(i3[0][oosm], srs, n_trials), H6_dsr=dsr(h6[0][oosm], srs, n_trials))
    out["_meta"] = dict(n_trials_cumulative=n_trials, last=str(dates[-1].date()), sessions=N)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v5.json"), "w"), indent=1, default=str)
    print("refresh", {k:(v['sharpe'] if isinstance(v,dict) else v) for k,v in out["_refresh"].items()}, "trials", n_trials)
