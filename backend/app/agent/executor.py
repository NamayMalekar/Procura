"""The ONLY place that creates, changes or cancels purchase orders and moves budget.
live=False -> what-if mode used by the validator (supplier always says yes)
live=True  -> talks to the mock supplier API and records what really happened"""
from app.commons.enums import ActionType, POStatus
from app.integrations import supplier_api


def apply_action(store, a, live):
    kind = a["action"]
    if kind == ActionType.CREATE_PO:
        return _create(store, a, live)
    if kind == ActionType.AMEND_PO:
        return _amend(store, a)
    if kind == ActionType.CANCEL_PO:
        return _cancel(store, a)
    raise ValueError(f"unknown action '{kind}'")


def _create(store, a, live):
    sku, node, sid, qty = a["sku"], a["node"], a["supplier_id"], int(a["qty"])
    item = store.supplier_item(sid, sku)
    price = item["unit_price"]
    store.adjust_budget(sku, -qty * price)                       # reserve the money
    po = {"id": store.new_po_id(), "sku": sku, "node": node, "supplier_id": sid, "qty": qty,
          "unit_price": price, "status": POStatus.PLACED, "supplier_confirmed_qty": None,
          "eta_days": item["lead_time_days"], "created_by": "agent"}
    store.insert_po(po)
    result = {"action": ActionType.CREATE_PO, "po_id": po["id"], "supplier_id": sid, "requested": qty}
    if not live:
        store.update_po(po["id"], status=POStatus.CONFIRMED, supplier_confirmed_qty=qty)
        return {**result, "status": "confirmed", "confirmed": qty}
    resp = supplier_api.place_order(store, sid, sku, qty)
    if resp["status"] == "confirmed":
        store.update_po(po["id"], status=POStatus.CONFIRMED, supplier_confirmed_qty=resp["confirmed_qty"])
    elif resp["status"] == "partial":
        store.update_po(po["id"], status=POStatus.PARTIAL, supplier_confirmed_qty=resp["confirmed_qty"])
    else:                                                        # rejected: give the money back
        store.update_po(po["id"], status=POStatus.REJECTED)
        store.adjust_budget(sku, qty * price)
    store.log("create_po", po_id=po["id"], supplier=sid, qty=qty, result=resp["status"])
    return {**result, "status": resp["status"], "confirmed": resp.get("confirmed_qty"),
            "reason": resp.get("reason"), "detail": resp.get("detail")}


def _amend(store, a):
    po, new = store.po(a["po_id"]), int(a["qty"])
    ceiling = store.po_qty(po)
    if new < 0 or new > ceiling:
        raise ValueError(f"cannot amend {po['id']} to {new}: supplier ceiling is {ceiling}")
    store.adjust_budget(po["sku"], (po["qty"] - new) * po["unit_price"])
    store.update_po(po["id"], qty=new, supplier_confirmed_qty=new,
                    status=POStatus.CONFIRMED if new > 0 else POStatus.CANCELLED)
    store.log("amend_po", po_id=po["id"], qty=new)
    return {"action": ActionType.AMEND_PO, "po_id": po["id"], "status": "ok", "confirmed": new}


def _cancel(store, a):
    po = store.po(a["po_id"])
    store.adjust_budget(po["sku"], store.po_qty(po) * po["unit_price"])
    store.update_po(po["id"], status=POStatus.CANCELLED)
    store.log("cancel_po", po_id=po["id"])
    return {"action": ActionType.CANCEL_PO, "po_id": po["id"], "status": "ok"}
