"""Quant v2 (2026-11-04): 10 new pre-registered hypotheses + H6 parameter-neighbourhood robustness.
Same engine, costs and scoring as v1 (backtest_v1.py). Cumulative trial count includes v1's 25."""
import numpy as np, pandas as pd, json, os
import backtest_v1 as b
from backtest_v1 import O, H, L, C, V, pc, DAY, dates, COST, intraday, swing, stats, years, score, mc_dd, dsr
N = len(dates); cv = DAY.c.values; ret = DAY.c.pct_change().values
rng_pos = ((DAY.c - DAY.l) / (DAY.h - DAY.l)).values

def N1_gapdown_after_down(lag=0, cost=COST, **k):          # long open->close
    def f(i):
        g = O[i,0] / pc[i] - 1
        return [(1, 0, 389, None)] if i > 1 and ret[i-1] < -0.01 and g < -0.003 else []
    return intraday(f, lag, cost)
def N2_two_down_streak(lag=0, cost=COST, **k):             # swing 3d
    e = [(i+1, i+3, 1, "c") for i in range(2, N-3) if ret[i] < 0 and ret[i-1] < 0 and (cv[i]/cv[i-2]-1) < -0.02]
    return swing(e, cost, lag)
def N3_nr7_orb(lag=0, cost=COST, **k):                     # ORB only after NR7 day
    rngs = (DAY.h - DAY.l).values
    nr7 = np.r_[[False]*7, [rngs[i] <= rngs[i-6:i+1].min() for i in range(7, N)]]
    base = b.H3_orb.__wrapped__ if hasattr(b.H3_orb, "__wrapped__") else None
    def f(i):
        if not nr7[i-1]: return []
        hi, lo = H[i,:30].max(), L[i,:30].min()
        up = np.where(H[i,30:] > hi)[0]; dn = np.where(L[i,30:] < lo)[0]
        if not len(up) and not len(dn): return []
        if len(up) and (not len(dn) or up[0] < dn[0]): return [(1, 30+up[0]+1, 389, lo)]
        return [(-1, 30+dn[0]+1, 389, hi)]
    return intraday(f, lag, cost)
def N4_weekend(lag=0, cost=COST, **k):                     # Fri close -> Mon open
    pnl = np.zeros(N); tr = []
    for i in range(1, N):
        if dates[i].weekday() == 0 and dates[i-1].weekday() == 4:
            xp = DAY.o1.iloc[i] if lag else DAY.o.iloc[i]
            r = xp / cv[i-1] - 1 - cost; pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr
def N5_lunch_fade(lag=0, cost=COST, **k):                  # fade 10:00->12:00 move over 12:00->14:00
    def f(i):
        r = C[i,149] / C[i,29] - 1
        return [(-np.sign(r), 150, 269, None)] if abs(r) > 0.002 else []
    return intraday(f, lag, cost)
def N6_close_at_low_bounce(lag=0, cost=COST, **k):         # prior close in bottom 10% of range -> long open->close
    def f(i):
        return [(1, 0, 389, None)] if rng_pos[i-1] < 0.1 else []
    return intraday(f, lag, cost)
def N7_bigup_fade(lag=0, cost=COST, **k):                  # mirror of H6
    e = [(i+1, i+3, -1, "c") for i in range(1, N-3) if ret[i] > 0.02]
    return swing(e, cost, lag)
def N8_opening_drive(lag=0, cost=COST, **k):               # first 5 min > 0.3% -> follow 09:35-10:30
    def f(i):
        r = C[i,4] / O[i,0] - 1
        return [(np.sign(r), 5, 59, None)] if abs(r) > 0.003 else []
    return intraday(f, lag, cost)
def N9_pre_holiday(lag=0, cost=COST, **k):                 # long open->close on the day before a weekday market holiday
    def f(i):
        if i+1 >= N: return []
        gap = (dates[i+1] - dates[i]).days
        hol = gap > 1 and not (dates[i].weekday() == 4 and gap == 3)
        return [(1, 0, 389, None)] if hol else []
    return intraday(f, lag, cost)
def N10_overnight_after_down(lag=0, cost=COST, **k):       # buy close of a < -1% day, sell next open
    pnl = np.zeros(N); tr = []
    for i in range(1, N):
        if ret[i-1] < -0.01:
            xp = DAY.o1.iloc[i] if lag else DAY.o.iloc[i]
            r = xp / cv[i-1] - 1 - cost; pnl[i] = r; tr.append((dates[i], r))
    return pnl, tr

HYP = {"N1_gapdown_after_down": N1_gapdown_after_down, "N2_two_down_streak": N2_two_down_streak, "N3_nr7_orb": N3_nr7_orb,
       "N4_weekend": N4_weekend, "N5_lunch_fade": N5_lunch_fade, "N6_close_at_low_bounce": N6_close_at_low_bounce,
       "N7_bigup_fade": N7_bigup_fade, "N8_opening_drive": N8_opening_drive, "N9_pre_holiday": N9_pre_holiday,
       "N10_overnight_after_down": N10_overnight_after_down}
H6_GRID = [(t, h) for t in (-0.015, -0.02, -0.025, -0.03) for h in (2, 3, 4, 5)]

if __name__ == "__main__":
    ism = np.array(dates <= b.IS_END); oosm = ~ism
    out = {}; daily = {}
    for name, fn in HYP.items():
        base = fn(); st = fn(lag=1, cost=2*COST)
        r = dict(IS=stats(*base, ism), OOS=stats(*base, oosm), OOS_stress=stats(*st, oosm), years=years(base[0]), mc_dd95_max=mc_dd(base[0], oosm))
        r["score"] = score(r["OOS"], r["years"]); out[name] = r; daily[name] = base[0][oosm]
        print(name, r["score"]["total"], "IS", r["IS"]["sharpe"], "OOS", r["OOS"]["sharpe"], r["OOS"]["trades"], "stress", r["OOS_stress"]["sharpe"], flush=True)
    grid = {}
    for t, h in H6_GRID:
        p, tr = b.H6_bigdown(thr=t, hold=h)
        grid[f"{t}_{h}"] = dict(IS=stats(p, tr, ism)["sharpe"], OOS=stats(p, tr, oosm)["sharpe"], OOS_trades=stats(p, tr, oosm)["trades"])
        daily[f"H6grid_{t}_{h}"] = p[oosm]
    # v1 base strategies re-run on refreshed data so the DSR pool covers every trial
    for name, fn in b.HYP.items(): daily["v1_" + name] = fn()[0][oosm]
    n_trials = 25 + 2*len(HYP) + len(H6_GRID)
    srs = [p.mean()/p.std() for p in daily.values() if p.std() > 0]
    for name in out: out[name]["dsr"], out[name]["sr0_ann"] = dsr(daily[name], srs, n_trials)
    h6 = daily["H6grid_-0.02_3"]; out["_H6_dsr_cumulative"] = dsr(h6, srs, n_trials)
    out["_H6_grid"] = grid; out["_meta"] = dict(n_trials_cumulative=n_trials, sessions=N, last=str(dates[-1].date()))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v2.json"), "w"), indent=1, default=str)
    print("H6 grid (IS/OOS sharpe, OOS trades):"); [print(" ", k, v) for k, v in grid.items()]
    print("H6 cumulative DSR", out["_H6_dsr_cumulative"], "trials", n_trials)
