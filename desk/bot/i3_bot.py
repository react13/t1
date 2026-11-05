"""I3 'overnight in uptrend' bot — Alpaca PAPER only, QQQ proxy for MNQ.

Strategy (desk/strategies/ranked.md #1): at ~15:45 ET, if QQQ's price is above its 200-day average (using the 15:45 price as
today's close), buy at the close (market-on-close) and sell at the next 09:30 open (market-on-open). Otherwise stay flat.
Re-test 2026-11-05: deciding at 15:45 instead of the close gives OOS Sharpe 1.02 vs 0.97 (same 900 nights).

Commands (ET):  python3 i3_bot.py evening   # 15:40-15:48: decide + place CLS buy
                python3 i3_bot.py morning   # 09:15-09:27: place OPG sell for last night's position; reconcile
                python3 i3_bot.py status
DRY RUN by default; --paper sends orders to the PAPER account. --asof=YYYY-MM-DD replays an evening (always dry).
Shares plumbing, risk tiers, kill switch, calendar and blackout list with h6_bot.py.
"""
import sys, math, json, datetime as dt, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h6_bot as base
from h6_bot import api, TRADE_URL, DATA_URL, SYMBOL, ET, log, send, blackout, risk_budget, kill_switch, calendar, daily_closes, append_log

P5_GAP = 0.0111        # 5th-pct overnight loss when filter is on (backtest 2016-2026, 15:45 decision) -> sizing denominator
STATE = os.path.join(base.HERE, "state_i3.json")
base.STATE = STATE                      # keep I3 state separate from H6
base.LOG = os.path.join(base.HERE, "trades_i3.csv")

def full_sessions(n_cal_days=320):
    today = base.now().date()
    return [d for d, o, c in calendar(str(today - dt.timedelta(days=n_cal_days)), str(today)) if o == "09:30" and c == "16:00"]

def closes_200(days):
    """SIP daily bars (split-adjusted) for the last 199 full sessions before today."""
    q = {"timeframe": "1Day", "start": days[0], "end": days[-1], "feed": "sip", "adjustment": "all", "limit": 1000}
    bars = api(DATA_URL, f"/v2/stocks/{SYMBOL}/bars", q=q).get("bars") or []
    return {b["t"][:10]: float(b["c"]) for b in bars}

def price_at_1545(d):
    """IEX latest trade when live; SIP 15:45 bar when replaying (--asof)."""
    if base.ASOF:
        start = dt.datetime.fromisoformat(d + "T15:45:00").replace(tzinfo=ET)
        q = {"timeframe": "1Min", "start": start.isoformat(), "end": (start + dt.timedelta(minutes=1)).isoformat(), "feed": "sip", "adjustment": "all"}
        want = start.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        b = [x for x in api(DATA_URL, f"/v2/stocks/{SYMBOL}/bars", q=q).get("bars") or [] if x["t"].startswith(want)]
        return float(b[0]["c"]) if b else None
    p, _ = base.latest_trade(); return p

def evening():
    s = base.load_state(); today = str(base.now().date())
    days = full_sessions()
    if not days or days[-1] != today: return log(f"{today} not a full session -> no trade")
    if s["position"]: return log(f"already holding {s['position']} (morning exit missed?) -> no new entry")
    if blackout(today): return log("blackout date -> no new overnight position (rule 5, conservative)")
    why = kill_switch(s, check_data=not base.ASOF)
    if why: return log(f"kill switch: {why}")
    prior = [d for d in days if d < today][-199:]
    cl = closes_200(prior)
    if len(cl) < 199: return log(f"only {len(cl)} daily closes -> no trade (data)")
    px = price_at_1545(today)
    if px is None: return log("no 15:45 price -> no trade")
    ma = (sum(cl[d] for d in prior) + px) / 200
    log(f"filter: price {px:.2f} vs 200-day avg {ma:.2f} -> {'ON' if px > ma else 'OFF'}")
    if px <= ma: return
    risk = risk_budget(s, today); qty = math.floor(risk / (px * P5_GAP))
    if qty < 1: return log(f"risk ${risk:.0f} too small -> skip")
    o = send({"symbol": SYMBOL, "qty": str(qty), "side": "buy", "type": "market", "time_in_force": "cls", "client_order_id": f"i3-buy-{today}"})
    s["position"] = {"qty": qty, "ref": px, "entry_day": today, "order": o.get("id"), "dry": not base.LIVE, "risk": risk}
    base.save_state(s); append_log([today, "BUY-CLS", qty, px, "", "", "", f"risk ${risk:.0f}; ma {ma:.2f}"])

def morning():
    s = base.load_state(); today = str(base.now().date()); p = s["position"]
    if not p: return log("flat")
    if p["dry"] and base.LIVE: return log("state holds a DRY-RUN position; clear state_i3.json before paper trading")
    send({"symbol": SYMBOL, "qty": str(p["qty"]), "side": "sell", "type": "market", "time_in_force": "opg", "client_order_id": f"i3-sell-{today}"})
    append_log([today, "SELL-OPG", p["qty"], "", "", "", "", f"entered {p['entry_day']}"])
    s["position"] = None; base.save_state(s)
    # fill reconciliation + loss streak: TODO in first paper week (needs real fills) — see PHASES.md

if __name__ == "__main__":
    cmd = (sys.argv[1:] or ["status"])[0]
    {"evening": evening, "morning": morning, "status": base.status}.get(cmd, lambda: print(__doc__))()
