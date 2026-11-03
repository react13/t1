"""Quant v1 backtests on QQQ (proxy for MNQ). Rules fixed a priori: NO parameter optimisation.
P&L unit: fraction of notional (1x), additive. Costs are ESTIMATES (see COST)."""
import pandas as pd, numpy as np, os, json, math
from statistics import NormalDist
N01 = NormalDist()
D = os.path.join(os.path.dirname(__file__), "..", "data")
R = pd.read_pickle(os.path.join(D, "qqq_rth.pkl")); DAY = pd.read_pickle(os.path.join(D, "qqq_daily.pkl"))
COST = 1.5e-4    # ESTIMATE round trip: MNQ ~$1.24 comm + 1 tick/side ~0.5bp; QQQ spread ~0.2bp; padded to 1.5bp
IS_END, OOS_START = "2021-12-31", "2022-01-01"
dates = DAY.index
# minute matrices: rows = day, cols = minute 0..389 (09:30..15:59)
R["k"] = R.m - 570
piv = {f: R.pivot_table(index="date", columns="k", values=f).reindex(columns=range(390)).ffill(axis=1) for f in "ohlcv"}
for f in piv: piv[f].index = pd.to_datetime(piv[f].index)
O, H, L, C, V = (piv[f].values for f in "ohlcv")
pc = DAY.c.shift(1).values

def intraday(sig_fn, lag, cost):
    """sig_fn(i) -> list of (side, entry_k, exit_k, stop) ; entry at open of bar entry_k+lag, exit at close of exit_k (or stop)."""
    pnl = np.zeros(len(dates)); trades = []
    for i in range(1, len(dates)):
        for side, ek, xk, stop in sig_fn(i):
            ek = ek + lag
            if ek > xk: continue
            ep = O[i, ek]; xp = C[i, xk]
            if stop is not None:   # stop checked bar by bar after entry
                seg_l, seg_h = L[i, ek:xk+1], H[i, ek:xk+1]
                hit = np.where(seg_l <= stop)[0] if side > 0 else np.where(seg_h >= stop)[0]
                if len(hit): xp = stop
            r = side * (xp / ep - 1) - cost
            pnl[i] += r; trades.append((dates[i], r))
    return pnl, trades

def swing(entries, cost, late):
    """entries: list of (i_entry, i_exit, side, exit_field) ; entry at open of day i (09:31 open if late), exit at open/close of i_exit."""
    pnl = np.zeros(len(dates)); trades = []; busy = -1
    for i, j, side, xf in entries:
        if i <= busy or i >= len(dates) or j >= len(dates): continue
        ep = DAY.o1.iloc[i] if late else DAY.o.iloc[i]
        prev = ep
        for d in range(i, j + 1):
            px = DAY[xf].iloc[d] if d == j else DAY.c.iloc[d]
            pnl[d] += side * (px - prev) / ep; prev = px
        pnl[i] -= cost
        trades.append((dates[j], side * (prev / ep - 1) - cost)); busy = j
    return pnl, trades

# ---------------- hypotheses ----------------
def H1_gapfade(lag=0, cost=COST, thr=0.005, **k):
    def f(i):
        g = O[i,0] / pc[i] - 1
        return [(-np.sign(g), 0, 389, None)] if abs(g) > thr else []
    return intraday(f, lag, cost)
def H2_gapgo(lag=0, cost=COST, thr=0.005, **k):
    def f(i):
        g = O[i,0] / pc[i] - 1
        return [(np.sign(g), 0, 389, None)] if abs(g) > thr else []
    return intraday(f, lag, cost)
def H3_orb(lag=0, cost=COST, use_stop=True, **k):
    def f(i):
        hi, lo = H[i,:30].max(), L[i,:30].min()
        up = np.where(H[i,30:] > hi)[0]; dn = np.where(L[i,30:] < lo)[0]
        if not len(up) and not len(dn): return []
        if len(up) and (not len(dn) or up[0] < dn[0]):
            return [(1, 30 + up[0] + 1, 389, lo if use_stop else None)]
        return [(-1, 30 + dn[0] + 1, 389, hi if use_stop else None)]
    return intraday(f, lag, cost)
def H4_firsthalf_lasthalf(lag=0, cost=COST, **k):
    def f(i):
        r1 = C[i,29] / pc[i] - 1     # prev close -> 10:00
        return [(np.sign(r1), 360, 389, None)] if r1 != 0 else []
    return intraday(f, lag, cost)
def H5_overnight(lag=0, cost=COST, **k):
    pnl = np.zeros(len(dates)); trades = []
    for i in range(1, len(dates)):
        ep = DAY.c.iloc[i-1]; xp = DAY.o1.iloc[i] if lag else DAY.o.iloc[i]
        r = xp / ep - 1 - cost; pnl[i] = r; trades.append((dates[i], r))
    return pnl, trades
def H6_bigdown(lag=0, cost=COST, thr=-0.02, hold=3, **k):
    ret = DAY.c.pct_change().values
    e = [(i+1, i+hold, 1, "c") for i in range(1, len(dates)-hold) if ret[i] < thr]
    return swing(e, cost, lag)
def H7_rsi2(lag=0, cost=COST, use_trend=True, **k):
    c = DAY.c; d = c.diff(); up = d.clip(lower=0).ewm(alpha=1/2, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/2, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).values; ma200 = c.rolling(200).mean().values; ma5 = c.rolling(5).mean().values; cv = c.values
    e = []
    for i in range(200, len(dates)-1):
        if rsi[i] < 10 and (cv[i] > ma200[i] or not use_trend):
            j = i + 1
            while j < len(dates)-1 and j < i + 5 and not cv[j] > ma5[j]: j += 1
            e.append((i+1, min(j+1, len(dates)-1), 1, "o"))   # condition seen at close j -> exit next open
    return swing(e, cost, lag)
def H8_vwap_fade(lag=0, cost=COST, use_time=True, **k):
    def f(i):
        tp = (H[i] + L[i] + C[i]) / 3; vv = np.nan_to_num(V[i]); cv = np.cumsum(vv)
        vw = np.cumsum(tp * vv) / np.where(cv > 0, cv, np.nan)
        dev = C[i] / vw - 1; sd = pd.Series(dev).expanding(30).std().values
        start = 60 if use_time else 30
        for k_ in range(start, 370):
            if abs(dev[k_]) > 2 * sd[k_] and sd[k_] > 0:
                side = -np.sign(dev[k_])
                tgt = np.where((C[i, k_+1:] - vw[k_+1:]) * side >= 0)[0]
                xk = k_ + 1 + tgt[0] if len(tgt) else 384
                return [(side, k_ + 1, min(xk, 384), None)]
        return []
    return intraday(f, lag, cost)
def H9_opex_week(lag=0, cost=COST, **k):
    e = []
    for i in range(len(dates)):
        d = dates[i]
        if d.weekday() == 4 and 15 <= d.day <= 21:          # 3rd Friday
            s = i
            while s > 0 and (d - dates[s-1]).days < 7 and dates[s-1].weekday() < dates[s].weekday(): s -= 1
            if s < i: e.append((s, i, 1, "c"))
    return swing(e, cost, lag)
def H10_turn_of_month(lag=0, cost=COST, **k):
    e = []; m = pd.Series(dates.month, index=range(len(dates)))
    for i in range(1, len(dates)-3):
        if m[i] != m[i+1]:   # i = last day of month -> enter its open? use next-day open to avoid lookahead on month end known in advance
            e.append((i, i+3, 1, "c"))   # month-end date is known in advance -> enter last day open, exit 3rd day of new month close
    return swing(e, cost, lag)
def H11_lateday_mom(lag=0, cost=COST, thr=0.01, **k):
    def f(i):
        r = C[i,269] / pc[i] - 1     # prev close -> 14:00
        return [(np.sign(r), 270, 389, None)] if abs(r) > thr else []
    return intraday(f, lag, cost)

HYP = {"H1_gap_fade": H1_gapfade, "H2_gap_go": H2_gapgo, "H3_orb30": H3_orb, "H4_first30_last30": H4_firsthalf_lasthalf,
       "H5_overnight": H5_overnight, "H6_bigdown_3d": H6_bigdown, "H7_rsi2_trend": H7_rsi2, "H8_vwap_fade": H8_vwap_fade,
       "H9_opex_week": H9_opex_week, "H10_turn_of_month": H10_turn_of_month, "H11_lateday_mom": H11_lateday_mom}
ABL = {"H3_orb30": [("no_stop", dict(use_stop=False))], "H7_rsi2_trend": [("no_trend_filter", dict(use_trend=False))],
       "H8_vwap_fade": [("no_time_filter", dict(use_time=False))]}

# ---------------- metrics ----------------
def maxdd(p):
    eq = np.cumsum(p); return float((np.maximum.accumulate(np.r_[0, eq])[1:] - eq).max())
def stats(pnl, trades, mask):
    p = pnl[mask]; tr = np.array([r for d, r in trades if mask[dates.get_loc(d)]])
    sr = p.mean() / p.std() * math.sqrt(252) if p.std() > 0 else 0
    ann = p.mean() * 252; dd = maxdd(p)
    t = tr.mean() / tr.std() * math.sqrt(len(tr)) if len(tr) > 1 and tr.std() > 0 else 0
    return dict(sharpe=round(sr, 2), ann_ret=round(ann*100, 2), maxdd=round(dd*100, 2), mar=round(ann/dd, 2) if dd > 0 else 0,
                trades=int(len(tr)), avg_bp=round(tr.mean()*1e4, 2) if len(tr) else 0, win=round((tr > 0).mean()*100, 1) if len(tr) else 0, t=round(t, 2))
def years(pnl):
    s = pd.Series(pnl, index=dates).groupby(dates.year).sum(); return {int(y): round(v*100, 2) for y, v in s.items()}
def bucket(x, cuts):  # cuts ascending -> score 1..5
    return 1 + sum(x > c for c in cuts)
def score(oos, yrs):
    pos = np.mean([v > 0 for v in yrs.values()])
    s = dict(sharpe=bucket(oos["sharpe"], [0, .5, 1, 1.5]), drawdown=bucket(oos["mar"], [0, .25, .5, 1]),
             trades=bucket(oos["trades"], [30, 60, 120, 250]), edge=bucket(oos["t"], [0, 1, 2, 3]),
             wf=bucket(pos, [.5, .6, .7, .849]))
    s["total"] = sum(s.values()); s["years_pos_pct"] = round(pos*100); return s
def mc_dd(pnl, mask, n=1000, seed=7):
    p = pnl[mask]; p = p[p != 0]; rng = np.random.default_rng(seed)
    dds = [maxdd(rng.choice(p, len(p), replace=True)) for _ in range(n)] if len(p) else [0]
    return round(np.percentile(dds, 95)*100, 2), round(max(dds)*100, 2)
def dsr(p, sr_trials, n):
    p = p[~np.isnan(p)]; T = len(p); sr = p.mean() / p.std()
    g = 0.5772156649; v = np.var(sr_trials)
    sr0 = math.sqrt(v) * ((1-g) * N01.inv_cdf(1 - 1/n) + g * N01.inv_cdf(1 - 1/(n*math.e)))
    sk = pd.Series(p).skew(); ku = pd.Series(p).kurt() + 3
    z = (sr - sr0) * math.sqrt(T-1) / math.sqrt(max(1e-9, 1 - sk*sr + (ku-1)/4 * sr**2))
    return round(N01.cdf(z), 3), round(sr0*math.sqrt(252), 2)

if __name__ == "__main__":
    ism = np.array(dates <= IS_END); oosm = ~ism
    out = {}; daily_oos = {}
    for name, fn in HYP.items():
        base = fn(); stress = fn(lag=1, cost=2*COST)
        res = dict(IS=stats(*base, ism), OOS=stats(*base, oosm), OOS_stress=stats(*stress, oosm), years=years(base[0]),
                   mc_dd95_max=mc_dd(base[0], oosm), abl={})
        res["score"] = score(res["OOS"], res["years"])
        for an, kw in ABL.get(name, []):
            a = fn(**kw); res["abl"][an] = dict(OOS=stats(*a, oosm), IS=stats(*a, ism))
        out[name] = res; daily_oos[name] = base[0][oosm]
        print(name, res["score"]["total"], res["IS"], res["OOS"], flush=True)
    ntr = len(HYP) + sum(len(v) for v in ABL.values()) + len(HYP)   # base + ablations + stress reruns
    srs = [p.mean()/p.std() for p in daily_oos.values() if p.std() > 0]
    for name in out: out[name]["dsr"], out[name]["sr0_ann"] = dsr(daily_oos[name], srs, ntr)
    out["_meta"] = dict(n_trials=ntr, cost_rt_bp=COST*1e4, sessions=len(dates), IS="2016-01-04..2021-12-31", OOS="2022-01-03..2026-11-02")
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_v1.json"), "w"), indent=1, default=str)
