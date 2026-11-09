"""Quant v7 (2026-11-09): 10 pre-registered ideas. Same engine/costs/scoring as v1. Rules fixed before running."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import O, H, L, C, pc, DAY, dates, COST, intraday, swing, stats, years, score, dsr
N=len(dates); cv=DAY.c.values; ov=DAY.o.values; hv=DAY.h.values; lv=DAY.l.values; ret=DAY.c.pct_change().values
ma200=DAY.c.rolling(200).mean().values; up=cv>ma200
def ovn(cond, lag=0, cost=COST):
    p=np.zeros(N); t=[]
    for i in range(201,N):
        if cond(i-1):
            xp=DAY.o1.iloc[i] if lag else ov[i]; r=xp/cv[i-1]-1-cost; p[i]=r; t.append((dates[i],r))
    return p,t
def orb5(i):
    hi,lo=H[i,:5].max(),L[i,:5].min(); u=np.where(H[i,5:]>hi)[0]; d=np.where(L[i,5:]<lo)[0]
    if not len(u) and not len(d): return []
    if len(u) and (not len(d) or u[0]<d[0]): return [(1,min(5+u[0]+1,389),389,lo)]
    return [(-1,min(5+d[0]+1,389),389,hi)]
T={
"T1":("I3 (overnight when above 200-day) but skip Friday nights",lambda lag=0,cost=COST: ovn(lambda j: up[j] and dates[j].weekday()!=4, lag, cost)),
"T2":("Overnight hold when close in bottom 30% of day range",lambda lag=0,cost=COST: ovn(lambda j: hv[j]>lv[j] and (cv[j]-lv[j])/(hv[j]-lv[j])<0.3, lag, cost)),
"T3":("Gap up >0.3% and 10:00 price above open -> long 10:00 to close",lambda lag=0,cost=COST: intraday(lambda i: [(1,30,389,None)] if O[i,0]/pc[i]-1>0.003 and C[i,29]>O[i,0] else [], lag, cost)),
"T4":("Lowest close in 5 days while above 200-day -> buy next open, hold 2 days",lambda lag=0,cost=COST: swing([(i+1,i+2,1,"c") for i in range(201,N-2) if up[i] and cv[i]<=cv[i-4:i+1].min()], cost, lag)),
"T5":("Lowest close in 10 days while above 200-day -> buy next open, hold 5 days",lambda lag=0,cost=COST: swing([(i+1,i+5,1,"c") for i in range(201,N-5) if up[i] and cv[i]<=cv[i-9:i+1].min()], cost, lag)),
"T6":("5-minute opening-range breakout, stop at other side, exit close",lambda lag=0,cost=COST: intraday(orb5, lag, cost)),
"T7":("Monday after a down Friday: long open->close",lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if dates[i].weekday()==0 and ret[i-1]<0 else [], lag, cost)),
"T8":("Every Tuesday: long open->close",lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if dates[i].weekday()==1 else [], lag, cost)),
"T9":("Every day: long the last hour (15:00-16:00)",lambda lag=0,cost=COST: intraday(lambda i: [(1,330,389,None)], lag, cost)),
"T10":("Every day: long the first hour (09:30-10:30)",lambda lag=0,cost=COST: intraday(lambda i: [(1,0,59,None)], lag, cost)),
}
if __name__=="__main__":
    ism=np.array(dates<=b.IS_END); oosm=~ism; out={}; daily={}
    for k,(desc,fn) in T.items():
        p,t=fn(); ps,ts=fn(lag=1,cost=2*COST)
        r=dict(desc=desc, IS=stats(p,t,ism), OOS=stats(p,t,oosm), OOS_stress=stats(ps,ts,oosm), years=years(p))
        r["score"]=score(r["OOS"],r["years"]); out[k]=r; daily[k]=p[oosm]
        print(f"{k:4s} score {r['score']['total']:>2}  IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4})  OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4})  stress {r['OOS_stress']['sharpe']:>5}  2022 {r['years'][2022]:>6}  {desc}", flush=True)
    for n,f in b.HYP.items(): daily["v1_"+n]=f()[0][oosm]
    nt=141+2*len(T); srs=[p.mean()/p.std() for p in daily.values() if p.std()>0]
    for k in out: out[k]["dsr"],_=dsr(daily[k],srs,nt)
    out["_meta"]=dict(n_trials_cumulative=nt,last=str(dates[-1].date()))
    json.dump(out,open(os.path.join(os.path.dirname(__file__),"results_v7.json"),"w"),indent=1,default=str); print("trials",nt)
