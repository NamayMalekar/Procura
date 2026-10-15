"""Read-only tools the agent can call to investigate. Each call is logged, so we can
later prove the agent looked at the right evidence. TOOL_SPECS describes them to the LLM."""
from . import config, planning


def _spec(name, desc, props, required):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": props, "required": required}}


S = {"type": "string"}
TOOL_SPECS = [
    _spec("get_inventory", "On-hand stock, safety stock, storage capacity and free storage for a SKU at a node.",
          {"sku": S, "node": S}, ["sku", "node"]),
    _spec("get_demand", "System forecast per day, last 14 days of real sales, and an assessment of whether "
          "recent sales are a sustained surge, a one-day spike, or normal.", {"sku": S, "node": S}, ["sku", "node"]),
    _spec("get_promotions", "Active or planned promotions for a SKU.", {"sku": S}, ["sku"]),
    _spec("get_open_pos", "Open purchase orders for a SKU at a node, including supplier-confirmed quantity.",
          {"sku": S, "node": S}, ["sku", "node"]),
    _spec("get_supplier_options", "Every supplier that sells the SKU: price, lead time, MOQ, case size, "
          "quantity available now, reliability, eligibility.", {"sku": S}, ["sku"]),
    _spec("get_budget", "Remaining purchasing budget for the SKU's category.", {"sku": S}, ["sku"]),
    _spec("calculate_replenishment", "Target stock, current position and units needed for a given supplier "
          "lead time. Optionally override incoming quantity (e.g. after amending a PO).",
          {"sku": S, "node": S, "lead_time_days": {"type": "integer"},
           "incoming_override": {"type": "integer"}}, ["sku", "node", "lead_time_days"]),
]


class ToolBox:
    def __init__(self, store):
        self.store = store
        self.log = []

    @property
    def called(self):
        return {c["tool"] for c in self.log}

    def call(self, name, **kw):
        if name not in {t["name"] for t in TOOL_SPECS}:
            return {"error": f"unknown tool {name}"}
        try:
            out = getattr(self, name)(**kw)
        except Exception as e:  # tool errors go back to the brain, not crash the run
            out = {"error": f"{type(e).__name__}: {e}"}
        self.log.append({"tool": name, "args": kw, "result": out})
        return out

    # ---- tools -------------------------------------------------------------
    def get_inventory(self, sku, node):
        inv = self.store.inventory(sku, node)
        return {**inv, "sku": sku, "node": node, "incoming_qty": self.store.incoming(sku, node),
                "storage_free": self.store.storage_free(sku, node)}

    def get_demand(self, sku, node):
        d = self.store.demand(sku, node)
        return {**d, "assessment": planning.demand_assessment(d["forecast_daily"], d["sales_last_14_days"])}

    def get_promotions(self, sku):
        return self.store.s["promotions"].get(sku, [])

    def get_open_pos(self, sku, node):
        return [{**p, "effective_qty": self.store.po_qty(p),
                 "supplier_shortfall": self.store.po_qty(p) < p["qty"]}
                for p in self.store.open_pos(sku, node)]

    def get_supplier_options(self, sku):
        primary = self.store.product(sku)["primary_supplier"]
        out = []
        for i in self.store.supplier_items(sku):
            sup = self.store.supplier(i["supplier_id"])
            out.append({"supplier_id": i["supplier_id"], "name": sup["name"], "unit_price": i["unit_price"],
                        "lead_time_days": i["lead_time_days"], "moq": i["moq"], "pack_size": i["pack_size"],
                        "available_qty": i["available_qty"], "reliability": sup["reliability"],
                        "is_primary": i["supplier_id"] == primary,
                        "eligible": sup["reliability"] >= config.MIN_SUPPLIER_RELIABILITY})
        return out

    def get_budget(self, sku):
        return {"category": self.store.product(sku)["category"], **self.store.budget(sku)}

    def calculate_replenishment(self, sku, node, lead_time_days, incoming_override=None):
        inv = self.store.inventory(sku, node)
        d = self.store.demand(sku, node)
        a = planning.demand_assessment(d["forecast_daily"], d["sales_last_14_days"])
        incoming = self.store.incoming(sku, node) if incoming_override is None else incoming_override
        position = inv["on_hand"] + incoming
        target = planning.target_position(a["effective_daily"], lead_time_days, inv["safety_stock"])
        return {"effective_daily_demand": a["effective_daily"], "demand_status": a["status"],
                "horizon_days": lead_time_days + config.REVIEW_PERIOD_DAYS, "target_position": target,
                "current_position": position, "need_qty": max(0, target - position),
                "max_cover_qty": planning.max_cover(target)}
