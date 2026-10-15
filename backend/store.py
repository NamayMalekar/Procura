"""In-memory 'database'. Holds the state dict and gives simple read helpers.
clone() makes a safe copy so the validator can test an action without touching real data."""
import copy
from . import data

OPEN_STATUSES = ("placed", "confirmed", "partial")


class Store:
    def __init__(self, state=None):
        self.s = state if state is not None else data.seed()

    def clone(self):
        return Store(copy.deepcopy(self.s))

    # ---- lookups -----------------------------------------------------------
    def product(self, sku):
        return self.s["products"][sku]

    def inventory(self, sku, node):
        return self.s["inventory"][sku][node]

    def demand(self, sku, node):
        return self.s["demand"][sku][node]

    def supplier(self, sid):
        return self.s["suppliers"][sid]

    def supplier_items(self, sku):
        return [i for i in self.s["supplier_items"] if i["sku"] == sku]

    def supplier_item(self, sid, sku):
        for i in self.s["supplier_items"]:
            if i["supplier_id"] == sid and i["sku"] == sku:
                return i
        raise KeyError(f"{sid} does not sell {sku}")

    def budget(self, sku):
        return self.s["budgets"][self.product(sku)["category"]]

    def po(self, po_id):
        return self.s["pos"][po_id]

    @staticmethod
    def po_qty(po):
        """Quantity we will really receive."""
        c = po.get("supplier_confirmed_qty")
        return po["qty"] if c is None else c

    def open_pos(self, sku, node):
        return [p for p in self.s["pos"].values()
                if p["sku"] == sku and p["node"] == node and p["status"] in OPEN_STATUSES]

    def incoming(self, sku, node):
        return sum(self.po_qty(p) for p in self.open_pos(sku, node))

    def storage_free(self, sku, node):
        inv = self.inventory(sku, node)
        return inv["storage_capacity"] - inv["on_hand"] - self.incoming(sku, node)

    def new_po_id(self):
        n = self.s["next_po"]
        self.s["next_po"] += 1
        return f"PO-{n}"

    def log(self, event, **kw):
        self.s["audit"].append({"event": event, **kw})
