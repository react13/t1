"""H6 'big down day' bot — Alpaca PAPER only, QQQ as proxy for MNQ signals.

Strategy (desk/strategies/ranked.md): if QQQ's last full session closed < -2% vs the session before,
buy at today's open (market-on-open), sell at the close of the 3rd trading day (market-on-close). One position at a time.

Commands (run on a schedule, ET):
  python3 h6_bot.py morning   # 09:20-09:27  check kill switches, signal, blackout -> place OPG buy
  python3 h6_bot.py guard     # every 5 min 09:35-15:45  daily-loss + stale-data checks; flatten if breached
  python3 h6_bot.py close     # 15:40-15:48  place CLS sell on exit day; reconcile fills, log P&L
  python3 h6_bot.py status    # print account, position, state
Default is DRY RUN (prints orders, sends nothing). Add --paper to send orders to the PAPER account.
Keys: env ALPACA_API_KEY / ALPACA_SECRET_KEY, else ~/.config/alpaca.env. Never stored in the repo.
"""
import os, sys, json, math, datetime as dt, urllib.request, urllib.parse
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
TRADE_URL = "https://paper-api.alpaca.markets"       # hard-coded PAPER. There is no live option in this file.
DATA_URL = "https://data.alpaca.markets"
SYMBOL = "QQQ"
SIGNAL_DROP = -0.02          # close-to-close trigger
HOLD_DAYS = 3                # entry day counts as day 1
P5_LOSS = 0.0351             # 5th-pct 3-day trade loss in backtest (143 trades, 2016-2026) -> sizing denominator
TIERS = {"A": 300, "B": 175, "C": 100, "Probe": 50}
TIER = "Probe"               # rules: first 2 weeks of paper = Probe; tiered sizing not yet proven -> never above flat $100
DAILY_LOSS_LIMIT = 350.0
MODEL_SLIP_BP = 0.75         # per side, matches backtest cost model (1.5 bp round trip)
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
LOG = os.path.join(HERE, "trades.csv")
LIVE = "--paper" in sys.argv and not any(a.startswith("--asof") for a in sys.argv)

# ---------- plumbing ----------
def keys():
    kf = os.path.expanduser("~/.config/alpaca.env")
    if "ALPACA_API_KEY" not in os.environ and os.path.exists(kf):
        for line in open(kf):
            k, _, v = line.strip().partition("=")
            if k: os.environ.setdefault(k, v)
    return {"APCA-API-KEY-ID": os.environ["ALPACA_API_KEY"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}

def api(base, path, method="GET", body=None, q=None):
    url = base + path + ("?" + urllib.parse.urlencode(q) if q else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={**keys(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        txt = r.read().decode(); return json.loads(txt) if txt else {}

ASOF = next((a.split("=")[1] for a in sys.argv if a.startswith("--asof=")), None)   # replay a past morning (dry-run only)
def now():
    if ASOF: return dt.datetime.fromisoformat(ASOF + "T09:20:00").replace(tzinfo=ET)
    return dt.datetime.now(ET)
def log(msg): print(f"{now():%Y-%m-%d %H:%M:%S} ET | {msg}", flush=True)
def load_state():
    s = json.load(open(STATE)) if os.path.exists(STATE) else {}
    s.setdefault("position", None); s.setdefault("losses_in_row", 0); s.setdefault("halted", None)
    s.setdefault("first_trade_date", None); s.setdefault("day", {}); return s
def save_state(s): json.dump(s, open(STATE, "w"), indent=1)

def calendar(start, end):
    """Alpaca market calendar -> list of (date, open, close). Used for holidays and early closes."""
    return [(c["date"], c["open"], c["close"]) for c in api(TRADE_URL, "/v2/calendar", q={"start": start, "end": end})]

def full_sessions_back(n_days=10):
    today = now().date()
    cal = calendar(str(today - dt.timedelta(days=20)), str(today))
    return [d for d, o, c in cal if o == "09:30" and c == "16:00"]

def daily_closes(dates):
    """Official-session closes from SIP 1-min bars (>15 min old, allowed on the free plan): last bar 15:59 ET."""
    out = {}
    for d in dates:
        start = dt.datetime.fromisoformat(d + "T15:59:00").replace(tzinfo=ET)
        q = {"timeframe": "1Min", "start": start.isoformat(), "end": (start + dt.timedelta(minutes=1)).isoformat(),
             "feed": "sip", "adjustment": "all", "limit": 5}
        bars = api(DATA_URL, f"/v2/stocks/{SYMBOL}/bars", q=q).get("bars") or []
        want = start.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        bars = [b for b in bars if b["t"].startswith(want)]        # exactly the 15:59 bar (backtest parity), not 16:00
        if bars: out[d] = float(bars[0]["c"])
    return out

def latest_trade():
    t = api(DATA_URL, f"/v2/stocks/{SYMBOL}/trades/latest", q={"feed": "iex"})["trade"]
    ts = dt.datetime.fromisoformat(t["t"].replace("Z", "+00:00").split(".")[0] + "+00:00" if "." in t["t"] else t["t"].replace("Z", "+00:00"))
    return float(t["p"]), ts

def blackout(d):
    for line in open(os.path.join(HERE, "blackout.txt")):
        if line.strip() and not line.startswith("#") and line.split()[0] == d: return True
    return False

def append_log(row):
    new = not os.path.exists(LOG)
    with open(LOG, "a") as f:
        if new: f.write("date,action,qty,ref_price,fill_price,slip_bp,pnl,note\n")
        f.write(",".join(str(x) for x in row) + "\n")

PAPER_START = "2026-11-11"   # owner approval (desk/briefs/decisions.md 2026-11-06): paper orders from Wed Nov 11, not before

def send(order):
    if LIVE and str(now().date()) < PAPER_START:
        log(f"BLOCKED (before approved paper start {PAPER_START}) would send " + json.dumps(order)); return {"id": "blocked", "status": "blocked"}
    log(("SEND " if LIVE else "DRY-RUN would send ") + json.dumps(order))
    return api(TRADE_URL, "/v2/orders", "POST", order) if LIVE else {"id": "dry-run", "status": "dry"}

STATE_FILES = ["state.json", "state_i3.json"]   # every bot on the desk; the $350 limit is DESK-WIDE

def desk_day(today):
    """Realized P&L and loss count for today summed over ALL bots' state files (both trade QQQ in one account)."""
    tot = {"realized": 0.0, "losses": 0}
    for f in STATE_FILES:
        fp = os.path.join(HERE, f)
        if os.path.exists(fp):
            d = json.load(open(fp)).get("day", {}).get(today, {})
            tot["realized"] += d.get("realized", 0.0); tot["losses"] += d.get("losses", 0)
    return tot

def risk_budget(s, today):
    """risk = min(tier, $350 - today's DESK-WIDE realized loss); after 2 desk losses today max tier C; never above flat $100 until tiers are proven."""
    d = desk_day(today)
    tier = TIERS[TIER]
    if d["losses"] >= 2: tier = min(tier, TIERS["C"])
    tier = min(tier, TIERS["C"])
    return max(0.0, min(tier, DAILY_LOSS_LIMIT + min(0.0, d["realized"])))

def kill_switch(s, check_data=True):
    if s["halted"]: return f"halted: {s['halted']}"
    if s["losses_in_row"] >= 3: return "3 losses in a row"
    if check_data:
        _, ts = latest_trade()
        age = (dt.datetime.now(dt.timezone.utc) - ts).total_seconds()
        if age > 120: return f"stale data: last IEX trade {age:.0f}s old (>120s)"
    return None

# ---------- commands ----------
def bar_price(d, hhmm, field):
    """SIP 1-min bar field at d hh:mm ET (model price for slippage)."""
    start = dt.datetime.fromisoformat(f"{d}T{hhmm}:00").replace(tzinfo=ET)
    q = {"timeframe": "1Min", "start": start.isoformat(), "end": (start + dt.timedelta(minutes=1)).isoformat(), "feed": "sip", "limit": 5}
    want = start.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
    b = [x for x in api(DATA_URL, f"/v2/stocks/{SYMBOL}/bars", q=q).get("bars") or [] if x["t"].startswith(want)]
    return float(b[0][field]) if b else None

def morning():
    s = load_state(); today = str(now().date())
    sessions = full_sessions_back()
    if not sessions or sessions[-1] != today:
        return log(f"{today} is not a full 09:30-16:00 session (holiday or early close) -> no trading")
    if s["position"]: return log(f"holding {s['position']} -> nothing to do this morning")
    prev = [d for d in sessions if d < today][-2:]
    closes = daily_closes(prev)
    if len(closes) < 2: return log(f"missing closes for {prev} -> no trade (data)")
    r = closes[prev[1]] / closes[prev[0]] - 1
    log(f"signal check: {prev[0]} {closes[prev[0]]} -> {prev[1]} {closes[prev[1]]} = {r*100:.2f}% (trigger < {SIGNAL_DROP*100:.0f}%)")
    if r >= SIGNAL_DROP: return log("no signal")
    if blackout(today): return log("SIGNAL but today is a tier-1 blackout date -> skip (rule 5)")
    why = kill_switch(s, check_data=False)   # pre-open: IEX has no fresh trades yet; stale check runs in guard
    if why: return log(f"SIGNAL but kill switch: {why}")
    risk = risk_budget(s, today)
    ref = closes[prev[1]]
    qty = math.floor(risk / (ref * P5_LOSS))
    if qty < 1: return log(f"risk ${risk:.0f} too small for 1 share at {ref} -> skip")
    exit_day = [d for d, o, c in calendar(today, str(now().date() + dt.timedelta(days=10))) if o == "09:30" and c == "16:00"][HOLD_DAYS - 1]   # full sessions only (CLS job runs 15:40; half-days close 13:00)
    o = send({"symbol": SYMBOL, "qty": str(qty), "side": "buy", "type": "market", "time_in_force": "opg",
              "client_order_id": f"h6-buy-{today}"})
    s["position"] = {"qty": qty, "ref": ref, "entry_day": today, "exit_day": exit_day, "order": o.get("id"), "dry": not LIVE, "risk": risk}
    s["first_trade_date"] = s["first_trade_date"] or today
    save_state(s); append_log([today, "BUY-OPG", qty, ref, "", "", "", f"risk ${risk:.0f}; exit {exit_day}"])

def guard():
    s = load_state(); today = str(now().date())
    why = kill_switch(s)
    # Own position only: the account's QQQ position can include other bots' shares (Alpaca nets per symbol).
    p = s["position"] if (s["position"] and not s["position"].get("dry")) else None
    if p:
        last, _ = latest_trade(); ref = p.get("fill") or p["ref"]
        upl = (last - ref) * p["qty"]                          # open P&L since entry (conservative vs intraday-only); realized = desk_day(today)["realized"]
        if realized + upl <= -DAILY_LOSS_LIMIT: why = why or f"daily loss limit: desk realized {realized:.0f} + H6 open {upl:.0f}"
    if why and why.startswith("stale") and not p:
        return log(f"guard: {why} but H6 holds nothing -> no halt (next morning run re-checks)")
    if why and why.startswith(("stale", "daily")):
        log(f"KILL SWITCH: {why} -> flatten H6's own shares and halt")
        if p: send({"symbol": SYMBOL, "qty": str(p["qty"]), "side": "sell", "type": "market", "time_in_force": "day", "client_order_id": f"h6-kill-{today}"})
        if p: s["position"] = None; s["pending_reconcile"] = {**p, "exit_day": today, "kill": True}
        s["halted"] = f"{today} {why}"; save_state(s)
    else:
        log(f"guard ok{' ('+why+')' if why else ''}")

def close():
    s = load_state(); today = str(now().date()); p = s["position"]
    if not p: return log("flat")
    if p["dry"] and LIVE: return log("state holds a DRY-RUN position; clear state.json before paper trading")
    if today < p["exit_day"]: return log(f"holding until {p['exit_day']}")
    send({"symbol": SYMBOL, "qty": str(p["qty"]), "side": "sell", "type": "market", "time_in_force": "cls", "client_order_id": f"h6-sell-{today}"})
    if LIVE:   # fills: buy filled at open; sell at close -> reconcile in next morning run
        s["pending_reconcile"] = p
    append_log([today, "SELL-CLS", p["qty"], "", "", "", "", "exit day"])
    s["position"] = None; save_state(s)

def reconcile():
    """Next morning: read fills, compute P&L and slippage vs model, update loss streak."""
    s = load_state(); p = s.get("pending_reconcile")
    if not p or not LIVE: return
    buy = api(TRADE_URL, f"/v2/orders:by_client_order_id", q={"client_order_id": f"h6-buy-{p['entry_day']}"})
    sid = f"h6-kill-{p['exit_day']}" if p.get("kill") else f"h6-sell-{p['exit_day']}"
    sell = api(TRADE_URL, f"/v2/orders:by_client_order_id", q={"client_order_id": sid})
    bf, sf = float(buy["filled_avg_price"]), float(sell["filled_avg_price"])
    pnl = (sf - bf) * p["qty"]
    mo, mc = bar_price(p["entry_day"], "09:30", "o"), bar_price(p["exit_day"], "15:59", "c")   # backtest's model prices
    slip = max(abs(bf / mo - 1), abs(sf / mc - 1)) * 1e4 if mo and mc else 0.0
    d = s["day"].setdefault(p["exit_day"], {"realized": 0.0, "losses": 0}); d["realized"] += pnl
    if pnl < 0: d["losses"] += 1; s["losses_in_row"] += 1
    else: s["losses_in_row"] = 0
    if slip > 3 * MODEL_SLIP_BP:        # kill switch: slippage > 3x model
        s["halted"] = f"{p['exit_day']} slippage {slip:.0f}bp"
    append_log([p["exit_day"], "RECONCILE", p["qty"], p["ref"], f"{bf}->{sf}", f"{slip:.1f}", f"{pnl:.2f}", ""])
    s.pop("pending_reconcile"); save_state(s)

def status():
    a = api(TRADE_URL, "/v2/account")
    log(f"PAPER account {a['status']} equity {a['equity']} cash {a['cash']} | mode {'PAPER-SEND' if LIVE else 'DRY-RUN'}")
    log(f"state: {json.dumps(load_state())}")

if __name__ == "__main__":
    cmd = (sys.argv[1:] or ["status"])[0]
    if cmd == "morning": reconcile(); morning()
    elif cmd in ("guard", "close", "status"): globals()[cmd]()
    else: print(__doc__)
