"""Offline tests for the paper bots: fake Alpaca API, no network, no orders. Run: python3 -I desk/bot/tests/test_bots.py"""
import os, sys, json, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
os.environ.setdefault("ALPACA_API_KEY", "test"); os.environ.setdefault("ALPACA_SECRET_KEY", "test")
import h6_bot as base
tmp = tempfile.mkdtemp(); shutil.copy(os.path.join(base.HERE, "blackout.txt"), tmp); base.HERE = tmp
import i3_bot
i3_bot.STATE = base.STATE = os.path.join(tmp, "state_i3.json"); base.LOG = os.path.join(tmp, "trades_i3.csv")
base.LIVE = True; sent = []
FILLS = {}
def fake_api(url, path, method="GET", body=None, q=None):
    if method == "POST": sent.append(body); return {"id": "x", "status": "accepted"}
    if "by_client_order_id" in path: return FILLS[q["client_order_id"]]
    if "/bars" in path:   # model prices
        hh = q["start"][11:16]; px = {"15:59": 600.00, "09:30": 603.00}.get(hh)
        from datetime import datetime, timezone
        t = datetime.fromisoformat(q["start"]).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M")
        return {"bars": [{"t": t + ":00Z", "o": px, "c": px}]}
    raise AssertionError(path)
base.api = i3_bot.api = fake_api
ok = 0
def check(cond, msg):
    global ok; assert cond, msg; ok += 1; print("PASS", msg)

# 1. I3 winning trade reconciles, books P&L, resets streak
json.dump({"position": None, "losses_in_row": 2, "halted": None, "first_trade_date": None, "day": {},
           "pending_reconcile": {"qty": 6, "ref": 600, "entry_day": "2026-11-11", "exit_day": "2026-11-12", "dry": False}}, open(base.STATE, "w"))
FILLS.update({"i3-buy-2026-11-11": {"status": "filled", "filled_avg_price": "600.01", "filled_qty": "6"},
              "i3-sell-2026-11-12": {"status": "filled", "filled_avg_price": "603.02", "filled_qty": "6"}})
i3_bot.reconcile(); s = json.load(open(base.STATE))
check(abs(s["day"]["2026-11-12"]["realized"] - 18.06) < 1e-6, "I3 win booked $18.06 on exit day")
check(s["losses_in_row"] == 0 and not s["halted"] and "pending_reconcile" not in s, "I3 win resets streak, no halt")

# 2. three losses in a row -> kill switch
for n, (e, x) in enumerate([("2026-11-12","2026-11-13"), ("2026-11-13","2026-11-16"), ("2026-11-16","2026-11-17")]):
    s = json.load(open(base.STATE)); s["pending_reconcile"] = {"qty": 6, "ref": 600, "entry_day": e, "exit_day": x, "dry": False}; json.dump(s, open(base.STATE, "w"))
    FILLS.update({f"i3-buy-{e}": {"status": "filled", "filled_avg_price": "600.00", "filled_qty": "6"},
                  f"i3-sell-{x}": {"status": "filled", "filled_avg_price": "603.00", "filled_qty": "6"}})
    FILLS[f"i3-sell-{x}"]["filled_avg_price"] = "599.00"   # loss; slippage vs 603 model open is large -> also tests slip halt
    i3_bot.reconcile()
s = json.load(open(base.STATE))
check(s["losses_in_row"] == 3, "three losses counted")
check(base.kill_switch(s, check_data=False) is not None, "kill switch fires (3 losses or slippage)")

check(base.kill_switch({"halted": None, "losses_in_row": 3}, check_data=False) == "3 losses in a row", "3 losses alone fire the kill switch")
check(base.kill_switch({"halted": None, "losses_in_row": 2}, check_data=False) is None, "2 losses do not")
# start-date guard: a LIVE send before Nov 11 is blocked
base.ASOF = "2026-11-10"                      # freeze the clock: the guard must block on the day before the start
r = base.send({"symbol": "QQQ", "qty": "1", "side": "buy"})
base.ASOF = None
check(r["status"] == "blocked" and len(sent) == 0, "paper order before 2026-11-11 is blocked")
# 3. unfilled order halts instead of guessing
json.dump({"position": None, "losses_in_row": 0, "halted": None, "first_trade_date": None, "day": {},
           "pending_reconcile": {"qty": 6, "ref": 600, "entry_day": "2026-11-18", "exit_day": "2026-11-19", "dry": False}}, open(base.STATE, "w"))
FILLS.update({"i3-buy-2026-11-18": {"status": "canceled", "filled_avg_price": None}, "i3-sell-2026-11-19": {"status": "filled", "filled_avg_price": "1", "filled_qty": "6"}})
i3_bot.reconcile(); s = json.load(open(base.STATE))
check(s["halted"] and "not both filled" in s["halted"], "unfilled order -> halt for owner check")

# 3b. expired MOC buy -> morning sends NO sell (would be a short), clears position, halts
json.dump({"position": {"qty": 6, "ref": 691, "entry_day": "2026-11-11", "order": "x", "dry": False, "risk": 50},
           "losses_in_row": 0, "halted": None, "first_trade_date": None, "day": {}}, open(base.STATE, "w"))
FILLS["i3-buy-2026-11-11"] = {"status": "expired", "filled_avg_price": None, "filled_qty": "0"}
n0 = len(sent); i3_bot.morning(); s = json.load(open(base.STATE))
check(len(sent) == n0 and s["position"] is None and "expired" in (s["halted"] or ""), "expired MOC buy -> no OPG sell, flat, halted")

# 4. desk-wide daily budget: an I3 loss today shrinks H6's risk budget
json.dump({"day": {"2026-11-20": {"realized": -300.0, "losses": 1}}}, open(os.path.join(tmp, "state_i3.json"), "w"))
json.dump({"position": None, "losses_in_row": 0, "halted": None, "day": {}}, open(os.path.join(tmp, "state.json"), "w"))
check(base.risk_budget({"day": {}}, "2026-11-20") == 50.0, "budget = min($50 tier, $350-300=$50)")
json.dump({"day": {"2026-11-20": {"realized": -330.0, "losses": 1}}}, open(os.path.join(tmp, "state_i3.json"), "w"))
check(base.risk_budget({"day": {}}, "2026-11-20") == 20.0, "after -$330 desk loss, H6 budget is $20 (desk-wide $350)")
check(len(sent) == 0, "no orders were sent by any test")
c = base.mnq_cols(["d","RECONCILE",6,"","","","18.06",""])
check(c[0]=="0.073" and abs(float(c[1]) - 18.06/6*82.6) < 0.05, "MNQ reporting columns: 6 sh = 0.073 MNQ, P&L scaled per contract")
log = open(base.LOG).read().splitlines(); check(log[0].endswith("mnq_equiv_contracts,pnl_per_1_mnq"), "trade log has MNQ columns")
print(f"\n{ok} checks passed"); shutil.rmtree(tmp)
