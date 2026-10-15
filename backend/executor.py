"""The ONLY place that changes purchase orders and budgets.
live=False  -> what-if mode used by the validator (supplier always says yes)
live=True   -> talks to the mock supplier API and records what really happened"""
from . import supplier_api


def apply_action(store, a, live):
    kind = a["action"]
    if kind == "create_po":
        return _create(store, a, live)
    if kind == "amend_po":
        return _amend(store, a)
    if kind == "cancel_po":
        return _cancel(store, a)
    raise ValueError(f"unknown action '{kind}'")


def _create(store, a, live):
    sku, node, sid, qty = a["sku"], a["node"], a["supplier_id"], int(a["qty"])
    item = store.supplier_item(sid, sku)
    price = item["unit_price"]
    budget = store.budget(sku)
    budget["remaining"] = round(budget["remaining"] - qty * price, 2)
    po = {"id": store.new_po_id(), "sku": sku, "node": node, "supplier_id": sid, "qty": qty,
          "unit_price": price, "status": "placed", "supplier_confirmed_qty": None,
          "eta_days": item["lead_time_days"], "created_by": "agent"}
    store.s["pos"][po["id"]] = po
    result = {"action": "create_po", "po_id": po["id"], "supplier_id": sid, "requested": qty}
    if not live:
        po["status"], po["supplier_confirmed_qty"] = "confirmed", qty
        return {**result, "status": "confirmed", "confirmed": qty}
    resp = supplier_api.place_order(store, sid, sku, qty)
    if resp["status"] == "confirmed":
        po["status"], po["supplier_confirmed_qty"] = "confirmed", resp["confirmed_qty"]
    elif resp["status"] == "partial":
        po["status"], po["supplier_confirmed_qty"] = "partial", resp["confirmed_qty"]
    else:  # rejected: give the money back
        po["status"] = "rejected"
        budget["remaining"] = round(budget["remaining"] + qty * price, 2)
    store.log("create_po", po_id=po["id"], supplier=sid, qty=qty, result=resp["status"])
    return {**result, "status": resp["status"], "confirmed": resp.get("confirmed_qty"),
            "reason": resp.get("reason"), "detail": resp.get("detail")}


def _amend(store, a):
    po = store.po(a["po_id"])
    new = int(a["qty"])
    ceiling = store.po_qty(po)
    if new < 0 or new > ceiling:
        raise ValueError(f"cannot amend {po['id']} to {new}: supplier ceiling is {ceiling}")
    store.budget(po["sku"])["remaining"] = round(
        store.budget(po["sku"])["remaining"] + (po["qty"] - new) * po["unit_price"], 2)
    po["qty"], po["supplier_confirmed_qty"] = new, new
    po["status"] = "confirmed" if new > 0 else "cancelled"
    store.log("amend_po", po_id=po["id"], qty=new)
    return {"action": "amend_po", "po_id": po["id"], "status": "ok", "confirmed": new}


def _cancel(store, a):
    po = store.po(a["po_id"])
    store.budget(po["sku"])["remaining"] = round(
        store.budget(po["sku"])["remaining"] + store.po_qty(po) * po["unit_price"], 2)
    po["status"] = "cancelled"
    store.log("cancel_po", po_id=po["id"])
    return {"action": "cancel_po", "po_id": po["id"], "status": "ok"}
