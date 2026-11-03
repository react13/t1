"""Build RTH minute panel + daily table from desk/data/QQQ_1min.csv.gz (Alpaca SIP, split-adjusted).
Output: desk/data/qqq_rth.pkl (minute) and desk/data/qqq_daily.pkl. Half-days and partial sessions are dropped."""
import pandas as pd, numpy as np, os
D = os.path.join(os.path.dirname(__file__), "..", "data")
df = pd.read_csv(os.path.join(D, "QQQ_1min.csv.gz"), usecols=["t","o","h","l","c","v"])
df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York")
df["date"] = df["t"].dt.date
df["m"] = df["t"].dt.hour * 60 + df["t"].dt.minute
r = df[(df.m >= 570) & (df.m < 960)].copy()
g = r.groupby("date")
info = g.agg(n=("m","size"), first=("m","min"), last=("m","max"))
full = info[(info.n >= 370) & (info["first"] == 570) & (info["last"] == 959)].index
dropped = info.index.difference(full)
r = r[r.date.isin(full)]
day = r.groupby("date").agg(o=("o","first"), h=("h","max"), l=("l","min"), c=("c","last"), v=("v","sum"))
o1 = r[r.m == 571].set_index("date")["o"]; day["o1"] = o1           # 09:31 open (1 bar late)
day.index = pd.to_datetime(day.index)
r.to_pickle(os.path.join(D, "qqq_rth.pkl")); day.to_pickle(os.path.join(D, "qqq_daily.pkl"))
print("full sessions", len(full), "dropped (half-day/partial)", len(dropped), "range", day.index.min().date(), day.index.max().date())
print("dropped sample", [str(x) for x in list(dropped)[:12]])
