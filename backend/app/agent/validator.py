"""The guardrail. Plain code, no LLM. It decides whether a proposal is safe to run (validate)
and whether what really happened matches what we expected (verify)."""
from app.commons.enums import ActionType, CaseType, Decision
from app.commons.money import cents
from app.core.policy import policy
from app.domain import planning
from .executor import apply_action

DECISIONS, ACTIONS = Decision.ALL, ActionType.ALL

# Tools the agent MUST have used before we trust its decision.
EVIDENCE = {
    CaseType.RECOMMENDATION: {"get_inventory", "get_demand", "get_open_pos", "get_supplier_options", "get_budget"},
    CaseType.SHORTFALL: {"get_inventory", "get_demand", "get_open_pos", "get_supplier_options", "get_budget"},
    CaseType.DEMAND_ALERT: {"get_inventory", "get_demand", "get_open_pos", "get_supplier_options", "get_budget"},
}


def _v(code, msg):
    return {"code": code, "message": msg}


def metrics(store, case, lead):
    sku, node = case["sku"], case["node"]
    inv, dem = store.inventory(sku, node), store.demand(sku, node)
    a = planning.demand_assessment(dem["forecast_daily"], dem["sales_last_14_days"])
    incoming = store.incoming(sku, node)
    position = inv["on_hand"] + incoming
    target = planning.target_position(a["effective_daily"], lead, inv["safety_stock"])
    return {"on_hand": inv["on_hand"], "incoming": incoming, "position": position, "target": target,
            "capacity": inv["storage_capacity"], "max_cover": planning.max_cover(target),
            "shortfall": max(0, target - position), "budget_remaining": store.budget(sku)["remaining"],
            "lead_time_days": lead}


def check_state(before, after, has_escalation):
    """Rules every resulting state must obey."""
    out = []
    if cents(after["budget_remaining"]) < 0:
        out.append(_v("BUDGET_EXCEEDED", f"Budget would go to {after['budget_remaining']:.2f}."))
    grew = after["incoming"] > before["incoming"]
    if grew and after["position"] > after["capacity"]:
        out.append(_v("STORAGE_EXCEEDED",
                      f"Stock would reach {after['position']} but storage holds {after['capacity']}."))
    if grew and after["position"] > after["max_cover"]:
        out.append(_v("OVERSTOCK", f"Stock would reach {after['position']}, above the allowed "
                                   f"maximum of {after['max_cover']} (target {after['target']})."))
    if after["shortfall"] > 0 and not has_escalation:
        out.append(_v("UNADDRESSED_SHORTFALL",
                      f"Stock stays {after['shortfall']} units below target and no escalation was raised."))
    return out


def _sells(store, sid, sku):
    try:
        store.supplier_item(sid, sku)
        return True
    except KeyError:
        return False


def _lead(store, case, actions):
    leads = [store.supplier_item(a["supplier_id"], a["sku"])["lead_time_days"]
             for a in actions if a.get("action") == "create_po"
             and _sells(store, a.get("supplier_id"), a.get("sku"))]
    if leads:
        return max(leads)
    primary = store.product(case["sku"])["primary_supplier"]
    return store.supplier_item(primary, case["sku"])["lead_time_days"]


def validate(store, case, proposal, called_tools):
    v = []
    d, actions = proposal.get("decision"), proposal.get("actions") or []
    esc = proposal.get("escalation")
    if d not in DECISIONS:
        v.append(_v("BAD_DECISION", f"decision must be one of {DECISIONS}"))
    if not proposal.get("rationale"):
        v.append(_v("NO_RATIONALE", "A written rationale is required."))
    missing = EVIDENCE.get(case["type"], set()) - set(called_tools)
    if missing:
        v.append(_v("MISSING_EVIDENCE", f"Not investigated: {sorted(missing)}"))
    if d in ("investigate", "escalate") and not esc:
        v.append(_v("NO_ESCALATION", f"'{d}' needs an escalation note for the buyer."))
    if d == "reject" and any(a.get("action") == "create_po" for a in actions):
        v.append(_v("INCONSISTENT", "A rejection cannot create purchase orders."))
    if d in ("accept",) and not any(a.get("action") == "create_po" for a in actions):
        v.append(_v("INCONSISTENT", "'accept' must create a purchase order."))

    total_cost = 0.0
    for a in actions:
        k = a.get("action")
        if k not in ACTIONS:
            v.append(_v("BAD_ACTION", f"unknown action {k}"))
            continue
        if k == "create_po":
            if (a.get("sku"), a.get("node")) != (case["sku"], case["node"]):
                v.append(_v("SCOPE_VIOLATION", "Order is outside the SKU/node of this case."))
                continue
            try:
                item = store.supplier_item(a["supplier_id"], a["sku"])
            except KeyError:
                v.append(_v("UNKNOWN_SUPPLIER", f"{a.get('supplier_id')} does not sell {a.get('sku')}."))
                continue
            q = a.get("qty")
            if not isinstance(q, int) or q <= 0:
                v.append(_v("BAD_QTY", "qty must be a positive integer."))
                continue
            sup = store.supplier(a["supplier_id"])
            if sup["reliability"] < policy.min_supplier_reliability:
                v.append(_v("SUPPLIER_UNRELIABLE", f"{a['supplier_id']} reliability {sup['reliability']} is too low."))
            if q % item["pack_size"]:
                v.append(_v("PACK_SIZE", f"{q} is not a multiple of case size {item['pack_size']}."))
            if q < item["moq"]:
                v.append(_v("BELOW_MOQ", f"{q} is below the supplier minimum of {item['moq']}."))
            if q > item["available_qty"]:
                v.append(_v("SUPPLIER_CAPACITY", f"Supplier has only {item['available_qty']} available."))
            total_cost += q * item["unit_price"]
        else:
            po = store.find_po(a.get("po_id"))
            if not po or (po["sku"], po["node"]) != (case["sku"], case["node"]):
                v.append(_v("BAD_PO", f"{a.get('po_id')} not found for this SKU/node."))

    if v:
        return {"ok": False, "violations": v, "requires_approval": False, "total_cost": total_cost,
                "metrics": None}

    lead = _lead(store, case, actions)
    before = metrics(store, case, lead)
    sim = store.clone()
    try:
        for a in actions:
            apply_action(sim, a, live=False)
    except Exception as e:
        return {"ok": False, "violations": [_v("SIMULATION_FAILED", str(e))], "requires_approval": False,
                "total_cost": total_cost, "metrics": None}
    after = metrics(sim, case, lead)
    v += check_state(before, after, bool(esc))
    return {"ok": not v, "violations": v, "total_cost": round(total_cost, 2),
            "requires_approval": total_cost > policy.approval_threshold,
            "metrics": {"before": before, "after": after}}


def verify(store, case, proposal, results, vmetrics):
    """After executing for real: did we get what we expected?"""
    issues = []
    for r in results:
        if r["status"] == "rejected":
            issues.append(_v("ORDER_REJECTED", f"{r['po_id']} rejected by supplier: {r.get('reason')} - {r.get('detail')}"))
        elif r["status"] == "partial":
            issues.append(_v("ORDER_PARTIAL", f"{r['po_id']}: supplier confirmed {r['confirmed']} of {r['requested']}."))
        elif r["status"] == "error":
            issues.append(_v("ACTION_ERROR", r.get("reason", "action failed")))
        elif r["action"] == "create_po":  # read the PO back from the system of record
            po = store.po(r["po_id"])
            if po["status"] != "confirmed" or po["qty"] != r["requested"]:
                issues.append(_v("PO_READBACK_MISMATCH", f"{po['id']} is {po['status']} qty {po['qty']}."))
    before, expected = vmetrics["before"], vmetrics["after"]
    actual = metrics(store, case, before["lead_time_days"])
    if actual["position"] != expected["position"]:
        issues.append(_v("POSITION_MISMATCH", f"Expected stock position {expected['position']}, got {actual['position']}."))
    issues += check_state(before, actual, bool(proposal.get("escalation")))
    seen, uniq = set(), []
    for i in issues:
        if (i["code"], i["message"]) not in seen:
            seen.add((i["code"], i["message"]))
            uniq.append(i)
    return {"ok": not uniq, "issues": uniq, "expected": expected, "actual": actual}
