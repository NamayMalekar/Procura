"""Mock supplier system. Real suppliers can say yes, partly yes, or no.
Failures are injected from seed_data.py through an `inject` field on a supplier item."""
from app.commons.packs import floor_pack


def place_order(store, supplier_id, sku, qty):
    item = store.supplier_item(supplier_id, sku)
    inj = item.get("inject")
    if inj and not inj.get("fired"):
        store.update_supplier_item(supplier_id, sku, inject={**inj, "fired": True})   # each failure fires once
        if inj["type"] == "price_change":
            store.update_supplier_item(supplier_id, sku, unit_price=inj["new_price"])
            return {"status": "rejected", "reason": "PRICE_CHANGED",
                    "detail": f"Quote is stale. New unit price is {inj['new_price']:.2f}."}
        if inj["type"] == "partial_once":
            c = floor_pack(int(qty * inj.get("fraction", 0.5)), item["pack_size"])
            store.update_supplier_item(supplier_id, sku, available_qty=item["available_qty"] - c)
            return {"status": "partial", "confirmed_qty": c,
                    "detail": f"Supplier can only ship {c} of {qty} right now."}
    if qty < item["moq"]:
        return {"status": "rejected", "reason": "BELOW_MOQ", "detail": f"MOQ is {item['moq']}."}
    if item["available_qty"] <= 0:
        return {"status": "rejected", "reason": "OUT_OF_STOCK", "detail": "Supplier has no stock."}
    if qty > item["available_qty"]:
        c = floor_pack(item["available_qty"], item["pack_size"])
        if c < item["moq"]:
            return {"status": "rejected", "reason": "BELOW_MOQ", "detail": "Available stock is below MOQ."}
        store.update_supplier_item(supplier_id, sku, available_qty=item["available_qty"] - c)
        return {"status": "partial", "confirmed_qty": c, "detail": f"Supplier can only ship {c} of {qty}."}
    store.update_supplier_item(supplier_id, sku, available_qty=item["available_qty"] - qty)
    return {"status": "confirmed", "confirmed_qty": qty}
