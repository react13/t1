"""Quant v6 (2026-11-08): 10 pre-registered intraday/calendar hypotheses. Same engine/costs/scoring as v1. Rules fixed before running."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import O, H, L, C, pc, DAY, dates, COST, intraday, swing, stats, years, score, mc_dd, dsr
N=len(dates); cv=DAY.c.values; ov=DAY.o.values; hv=DAY.h.values; lv=DAY.l.values; ret=DAY.c.pct_change().values
def ovn(cond, lag=0, cost=COST):
    p=np.zeros(N); t=[]
    for i in range(1,N):
        if cond(i-1):
            xp=DAY.o1.iloc[i] if lag else ov[i]; r=xp/cv[i-1]-1-cost; p[i]=r; t.append((dates[i],r))
    return p,t
def thanks_week(i):   # Mon-Wed of the week containing the 4th Thursday of November
    d=dates[i]
    if d.month!=11: return False
    th=[x for x in range(1,31) if __import__('datetime').date(d.year,11,x).weekday()==3][3]
    return th-3 <= d.day <= th-1
Q = {
"Q1": ("Down >1.5% from open by 15:00 -> long 15:00 to close", lambda lag=0,cost=COST: intraday(lambda i: [(1,330,389,None)] if C[i,329]/O[i,0]-1 < -0.015 else [], lag, cost)),
"Q2": ("Up >1.5% from open by 15:00 -> short 15:00 to close", lambda lag=0,cost=COST: intraday(lambda i: [(-1,330,389,None)] if C[i,329]/O[i,0]-1 > 0.015 else [], lag, cost)),
"Q3": ("First 15 min move >0.5% -> fade until 11:00", lambda lag=0,cost=COST: intraday(lambda i: [(-np.sign(C[i,14]/O[i,0]-1),15,89,None)] if abs(C[i,14]/O[i,0]-1)>0.005 else [], lag, cost)),
"Q4": ("After an inside day that closed up, long next open->close", lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if i>2 and hv[i-1]<=hv[i-2] and lv[i-1]>=lv[i-2] and cv[i-1]>ov[i-1] else [], lag, cost)),
"Q5": ("After 3 up days, short next open->close", lambda lag=0,cost=COST: intraday(lambda i: [(-1,0,389,None)] if i>3 and (ret[i-3:i]>0).all() else [], lag, cost)),
"Q6": ("After 3 down days, long next open->close", lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if i>3 and (ret[i-3:i]<0).all() else [], lag, cost)),
"Q7": ("Close in top 10% of day range -> hold overnight", lambda lag=0,cost=COST: ovn(lambda j: hv[j]>lv[j] and (cv[j]-lv[j])/(hv[j]-lv[j])>0.9, lag, cost)),
"Q8": ("Thanksgiving week: long Mon open -> Wed close", lambda lag=0,cost=COST: swing([(i, i+2, 1, "c") for i in range(N-2) if dates[i].weekday()==0 and thanks_week(i) and thanks_week(i+2)], cost, lag)),
"Q9": ("First trading day of the month: long open->close", lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if dates[i].month!=dates[i-1].month else [], lag, cost)),
"Q10":("Break of the 09:30-12:00 high after 12:00 -> long to close, stop at morning low", lambda lag=0,cost=COST: intraday(lambda i: (lambda hi,lo,up: [(1,150+up[0]+1,389,lo)] if len(up) and up[0]<239 else [])(H[i,:150].max(), L[i,:150].min(), np.where(H[i,150:]>H[i,:150].max())[0]), lag, cost)),
}
if __name__=="__main__":
    ism=np.array(dates<=b.IS_END); oosm=~ism; out={}; daily={}
    for k,(desc,fn) in Q.items():
        p,t=fn(); ps,ts=fn(lag=1,cost=2*COST)
        r=dict(desc=desc, IS=stats(p,t,ism), OOS=stats(p,t,oosm), OOS_stress=stats(ps,ts,oosm), years=years(p))
        r["score"]=score(r["OOS"],r["years"]); out[k]=r; daily[k]=p[oosm]
        print(f"{k:4s} score {r['score']['total']:>2}  IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4})  OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4})  stress {r['OOS_stress']['sharpe']:>5}  {desc}", flush=True)
    for n,f in b.HYP.items(): daily["v1_"+n]=f()[0][oosm]
    nt=121+2*len(Q); srs=[p.mean()/p.std() for p in daily.values() if p.std()>0]
    for k in out: out[k]["dsr"],_=dsr(daily[k],srs,nt)
    out["_meta"]=dict(n_trials_cumulative=nt, last=str(dates[-1].date()))
    json.dump(out, open(os.path.join(os.path.dirname(__file__),"results_v6.json"),"w"), indent=1, default=str); print("trials",nt)
