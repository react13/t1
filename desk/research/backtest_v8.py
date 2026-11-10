"""Quant v8 (2026-11-10): 10 pre-registered ideas around big up days, weekly momentum and moving-average crosses. Same engine/costs/scoring as v1."""
import numpy as np, json, os
import backtest_v1 as b
from backtest_v1 import O, C, pc, DAY, dates, COST, intraday, swing, stats, years, score, dsr
N=len(dates); cv=DAY.c.values; ov=DAY.o.values; ret=DAY.c.pct_change().values
ma200=DAY.c.rolling(200).mean().values; ma20=DAY.c.rolling(20).mean().values
def ovn(cond, lag=0, cost=COST):
    p=np.zeros(N); t=[]
    for i in range(201,N):
        if cond(i-1):
            xp=DAY.o1.iloc[i] if lag else ov[i]; r=xp/cv[i-1]-1-cost; p[i]=r; t.append((dates[i],r))
    return p,t
def week_ret(i): return cv[i]/cv[i-5]-1 if i>=5 else 0
def weekly(cond, hold_to_fri=True, lag=0, cost=COST):
    e=[]
    for i in range(6,N-1):
        if dates[i].weekday()==4 and cond(i):
            j=i+1; k=j
            if hold_to_fri:
                while k+1<N and dates[k+1].weekday()>dates[k].weekday(): k+=1
            e.append((j,k,1,"c"))
    return swing(e,cost,lag)
U={
"U1":("Day after a +3% day: long open->close (continuation)",lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if ret[i-1]>0.03 else [], lag, cost)),
"U2":("Day after a +3% day: short open->close (fade)",lambda lag=0,cost=COST: intraday(lambda i: [(-1,0,389,None)] if ret[i-1]>0.03 else [], lag, cost)),
"U3":("Overnight hold after a +2% day",lambda lag=0,cost=COST: ovn(lambda j: ret[j]>0.02, lag, cost)),
"U4":("Close within 1% below the 200-day avg -> long 3 days",lambda lag=0,cost=COST: swing([(i+1,i+3,1,"c") for i in range(201,N-3) if 0.99*ma200[i]<cv[i]<ma200[i]], cost, lag)),
"U5":("Gap up >1% after a down week -> long open->close",lambda lag=0,cost=COST: intraday(lambda i: [(1,0,389,None)] if i>6 and week_ret(i-1)<0 and O[i,0]/pc[i]-1>0.01 else [], lag, cost)),
"U6":("Prior week > +2% -> long Mon open to Fri close",lambda lag=0,cost=COST: weekly(lambda i: week_ret(i)>0.02, True, lag, cost)),
"U7":("Prior week < -2% -> long Monday open->close only",lambda lag=0,cost=COST: weekly(lambda i: week_ret(i)<-0.02, False, lag, cost)),
"U8":("Close back above 20-day avg after 5 days below -> long 3 days",lambda lag=0,cost=COST: swing([(i+1,i+3,1,"c") for i in range(30,N-3) if cv[i]>ma20[i] and (cv[i-5:i]<ma20[i-5:i]).all()], cost, lag)),
"U9":("Close below 20-day avg after 10 days above -> short 3 days",lambda lag=0,cost=COST: swing([(i+1,i+3,-1,"c") for i in range(30,N-3) if cv[i]<ma20[i] and (cv[i-10:i]>ma20[i-10:i]).all()], cost, lag)),
"U10":("I3 but only Mon-Wed nights",lambda lag=0,cost=COST: ovn(lambda j: cv[j]>ma200[j] and dates[j].weekday()<=2, lag, cost)),
}
if __name__=="__main__":
    ism=np.array(dates<=b.IS_END); oosm=~ism; out={}; daily={}
    for k,(desc,fn) in U.items():
        p,t=fn(); ps,ts=fn(lag=1,cost=2*COST)
        r=dict(desc=desc, IS=stats(p,t,ism), OOS=stats(p,t,oosm), OOS_stress=stats(ps,ts,oosm), years=years(p))
        r["score"]=score(r["OOS"],r["years"]); out[k]=r; daily[k]=p[oosm]
        print(f"{k:4s} score {r['score']['total']:>2}  IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4})  OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4})  stress {r['OOS_stress']['sharpe']:>5}  2022 {r['years'][2022]:>6}  {desc}", flush=True)
    for n,f in b.HYP.items(): daily["v1_"+n]=f()[0][oosm]
    nt=161+2*len(U); srs=[p.mean()/p.std() for p in daily.values() if p.std()>0]
    for k in out: out[k]["dsr"],_=dsr(daily[k],srs,nt)
    out["_meta"]=dict(n_trials_cumulative=nt,last=str(dates[-1].date()))
    json.dump(out,open(os.path.join(os.path.dirname(__file__),"results_v8.json"),"w"),indent=1,default=str); print("trials",nt)
