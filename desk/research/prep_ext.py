"""Extended-hours QQQ minute bars (04:00-20:00 ET) as a proxy for MNQ's ~23h session. Output: desk/data/qqq_ext.npz (ts ns, o, h, l, c)."""
import pandas as pd, numpy as np, os
D = os.path.join(os.path.dirname(__file__), "..", "data")
df = pd.read_csv(os.path.join(D, "QQQ_1min.csv.gz"), usecols=["t","o","h","l","c"])
df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York")
m = df["t"].dt.hour*60 + df["t"].dt.minute
df = df[(m >= 240) & (m < 1200)].sort_values("t")
np.savez(os.path.join(D, "qqq_ext.npz"), ts=df["t"].dt.tz_convert("UTC").values.astype("datetime64[ns]").astype(np.int64), o=df.o.values, h=df.h.values, l=df.l.values, c=df.c.values)
print("bars", len(df), df["t"].min(), df["t"].max())
