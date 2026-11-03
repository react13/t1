"""Pull 1-min SIP bars from Alpaca into desk/data/<SYM>_1min.csv.gz.
Keys: env ALPACA_API_KEY / ALPACA_SECRET_KEY, else ~/.config/alpaca.env (never stored in repo)."""
import os, sys, json, gzip, time, urllib.request, urllib.parse
_kf = os.path.expanduser("~/.config/alpaca.env")  # private, outside repo
if "ALPACA_API_KEY" not in os.environ and os.path.exists(_kf):
    for line in open(_kf):
        k, _, v = line.strip().partition("=")
        if k: os.environ.setdefault(k, v)
sym = sys.argv[1] if len(sys.argv) > 1 else "QQQ"
start = sys.argv[2] if len(sys.argv) > 2 else "2016-01-01T00:00:00Z"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_API_KEY"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
out = os.path.join(os.path.dirname(__file__), "..", "data", f"{sym}_1min.csv.gz")
tok, n = None, 0
with gzip.open(out, "wt") as f:
    f.write("t,o,h,l,c,v,n,vw\n")
    while True:
        q = {"timeframe": "1Min", "start": start, "limit": 10000, "feed": "sip", "adjustment": "all"}
        if tok: q["page_token"] = tok
        url = f"https://data.alpaca.markets/v2/stocks/{sym}/bars?" + urllib.parse.urlencode(q)
        for a in range(5):
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60)); break
            except Exception as e:
                time.sleep(2 ** a)
        else:
            sys.exit(f"failed at page token {tok}")
        for b in d.get("bars") or []:
            f.write(f'{b["t"]},{b["o"]},{b["h"]},{b["l"]},{b["c"]},{b["v"]},{b["n"]},{b["vw"]}\n'); n += 1
        tok = d.get("next_page_token")
        if not tok: break
        time.sleep(0.31)  # stay under 200 req/min
print(f"{sym}: {n} bars -> {out}")
