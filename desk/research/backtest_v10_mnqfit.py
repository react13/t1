"""Quant v10 (2026-11-11): 10 pre-registered INTRADAY ideas with a fixed 0.54% stop (~$300 per 1 MNQ at ~$55.7k notional, ESTIMATE),
flat by 16:00 -> risk per trade fits 1 MNQ inside the $350/day limit. Same engine/costs/scoring as v1. Rules fixed before running."""
import numpy as np, pandas as pd, json, os
import backtest_v1 as b
from backtest_v1 import O, H, L, C, V, pc, DAY, dates, COST, intraday, stats, years, score, dsr
N=len(dates); ret=DAY.c.pct_change().values; S=0.0054
def stp(i,k,side): e=O[i,k]; return e*(1-S) if side>0 else e*(1+S)
def M1(i):
    hi,lo=H[i,:30].max(),L[i,:30].min(); u=np.where(H[i,30:]>hi)[0]; d=np.where(L[i,30:]<lo)[0]
    if not len(u) and not len(d): return []
    if len(u) and (not len(d) or u[0]<d[0]): k=min(30+u[0]+1,389); return [(1,k,389,stp(i,k,1))]
    k=min(30+d[0]+1,389); return [(-1,k,389,stp(i,k,-1))]
def M2(i):
    g=O[i,0]/pc[i]-1; s=-np.sign(g); return [(s,0,389,stp(i,0,s))] if abs(g)>0.005 else []
def M3(i): return [(1,0,389,stp(i,0,1))] if O[i,0]/pc[i]-1<-0.005 else []
def M4(i):
    r=C[i,29]/O[i,0]-1; s=np.sign(r); return [(s,30,389,stp(i,30,s))] if abs(r)>0.002 else []
def M5(i):
    r=C[i,269]/pc[i]-1; s=np.sign(r); return [(s,270,389,stp(i,270,s))] if abs(r)>0.01 else []
def M6(i):
    r=C[i,4]/O[i,0]-1; s=np.sign(r); return [(s,5,389,stp(i,5,s))] if abs(r)>0.003 else []
def M7(i): return [(1,0,389,stp(i,0,1))] if i>1 and ret[i-1]<-0.02 else []
def M8(i): return [(1,0,389,stp(i,0,1))] if i>1 and ret[i-1]<-0.01 and O[i,0]/pc[i]-1<-0.003 else []
def M9(i):
    tp=(H[i]+L[i]+C[i])/3; vv=np.nan_to_num(V[i]); cv=np.cumsum(vv); vw=np.cumsum(tp*vv)/np.where(cv>0,cv,np.nan)
    if not (C[i,30:90]<vw[30:90]).all(): return []
    x=np.where(C[i,90:330]>vw[90:330])[0]
    if not len(x): return []
    k=90+x[0]+1; return [(1,k,389,stp(i,k,1))]
def M10(i):
    hi=H[i,:150].max(); u=np.where(H[i,150:]>hi)[0]
    if not len(u) or u[0]>=239: return []
    k=150+u[0]+1; return [(1,k,389,stp(i,k,1))]
DESC={"M1":"30-min opening-range breakout, 0.54% stop","M2":"Gap >0.5% fade, 0.54% stop","M3":"Gap down >0.5% buy, 0.54% stop",
"M4":"First 30 min >0.2% -> follow 10:00-close, 0.54% stop","M5":"Prior close->14:00 >1% -> follow to close, 0.54% stop",
"M6":"First 5 min >0.3% -> follow to close, 0.54% stop","M7":"Day after a -2% day: long open->close, 0.54% stop",
"M8":"After -1% day + gap down >0.3%: long open->close, 0.54% stop","M9":"Below VWAP 10:00-11:00 then reclaims it by 15:00 -> long to close, 0.54% stop",
"M10":"Break of 09:30-12:00 high after 12:00 -> long to close, 0.54% stop"}
F={k:globals()[k] for k in DESC}
if __name__=="__main__":
    ism=np.array(dates<=b.IS_END); oosm=~ism; out={}; daily={}
    for k,f in F.items():
        p,t=intraday(f,0,COST+1e-4); ps,ts=intraday(f,1,2*COST+1e-4)   # +1 bp for stop slippage
        r=dict(desc=DESC[k],IS=stats(p,t,ism),OOS=stats(p,t,oosm),OOS_stress=stats(ps,ts,oosm),years=years(p))
        r["score"]=score(r["OOS"],r["years"]); tro=np.array([x for d,x in t if d>pd.Timestamp(b.IS_END)])
        r["usd_per_MNQ"]=dict(avg=round(tro.mean()*55700,1), worst=round(tro.min()*55700,0)) if len(tro) else {}
        out[k]=r; daily[k]=p[oosm]
        print(f"{k:4s} score {r['score']['total']:>2} IS {r['IS']['sharpe']:>5} ({r['IS']['trades']:>4}) OOS {r['OOS']['sharpe']:>5} ({r['OOS']['trades']:>4}) stress {r['OOS_stress']['sharpe']:>5} $/MNQ {r['usd_per_MNQ']}  {DESC[k]}",flush=True)
    for n,f in b.HYP.items(): daily["v1_"+n]=f()[0][oosm]
    nt=193+2*len(F); srs=[p.mean()/p.std() for p in daily.values() if p.std()>0]
    for k in out: out[k]["dsr"],_=dsr(daily[k],srs,nt)
    out["_meta"]=dict(n_trials_cumulative=nt,last=str(dates[-1].date()))
    json.dump(out,open(os.path.join(os.path.dirname(__file__),"results_v10_mnqfit.json"),"w"),indent=1,default=str); print("trials",nt)
