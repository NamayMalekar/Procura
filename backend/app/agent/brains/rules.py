"""Offline brain: a deterministic buyer playbook. It uses the same tools as the LLM brain,
so the whole system runs with no API key. It is also the fallback if the LLM fails."""
from app.commons.money import cents
from app.commons.packs import ceil_pack, floor_pack
from app.core.policy import policy


class RulesBrain:
    name = "rules"

    def propose(self, case, tools, feedback=None):
        sku, node = case["sku"], case["node"]
        inv = tools.call("get_inventory", sku=sku, node=node)
        dem = tools.call("get_demand", sku=sku, node=node)
        promos = tools.call("get_promotions", sku=sku)
        pos = tools.call("get_open_pos", sku=sku, node=node)
        sups = tools.call("get_supplier_options", sku=sku)
        bud = tools.call("get_budget", sku=sku)
        a = dem["assessment"]
        factors, actions = [], []

        if feedback and feedback.get("execution_issues"):
            causes = [i["message"] for i in feedback["execution_issues"] if i["code"].startswith(("ORDER_", "ACTION_"))]
            factors.append("Re-planned after the last attempt failed: " +
                           "; ".join(causes or [i["message"] for i in feedback["execution_issues"]]))
        factors.append(f"Demand: forecast {a['forecast_daily']}/day, last-7-day average {a['avg_last_7']}/day "
                       f"-> {a['status'].replace('_', ' ')}, planning with {a['effective_daily']}/day"
                       + (" (no promotion explains it)." if a["status"] != "normal" and not promos else "."))

        # 1) fix open POs where the supplier is shipping less than we ordered
        refund = 0.0
        for po in pos:
            if po["supplier_shortfall"]:
                actions.append({"action": "amend_po", "po_id": po["id"], "qty": po["effective_qty"]})
                refund += (po["qty"] - po["effective_qty"]) * po["unit_price"]
                factors.append(f"{po['id']}: supplier ships {po['effective_qty']} of {po['qty']}; "
                               f"amend the PO to what is real and free ${(po['qty'] - po['effective_qty']) * po['unit_price']:.2f} of budget.")
        incoming = sum(p["effective_qty"] for p in pos)
        position = inv["on_hand"] + incoming
        budget_cents = cents(bud["remaining"] + refund)
        storage_free = inv["storage_capacity"] - inv["on_hand"] - incoming

        preferred = case.get("supplier_id") or next((s["supplier_id"] for s in sups if s["is_primary"]), None)
        base_lead = next(s["lead_time_days"] for s in sups if s["supplier_id"] == preferred)
        base = tools.call("calculate_replenishment", sku=sku, node=node,
                          lead_time_days=base_lead, incoming_override=incoming)
        factors.append(f"Stock position {position} (on hand {inv['on_hand']} + incoming {incoming}) vs target "
                       f"{base['target_position']} → real need {base['need_qty']} units.")

        escalation, chosen_qty, decision = None, 0, None
        if base["need_qty"] <= 0:
            if a["status"] in ("single_day_spike", "ambiguous"):
                decision = "investigate"
                escalation = {"reason": f"Sales look unusual (peak day {a['peak_day']} vs forecast {a['forecast_daily']}) "
                                        f"but only {a['elevated_days_of_7']} of 7 days are elevated, so it is not proven demand.",
                              "follow_up": "Ask store ops whether it was a one-off (bulk order, data error). "
                                           "Re-check after 2-3 more days of sales."}
                factors.append("Current stock plus open POs already cover the forecast; the spike is not enough evidence to buy more.")
            elif actions:
                decision = "modify"
                factors.append("Stock plus the reduced PO still covers demand, so no replacement order is needed.")
            else:
                decision = "reject"
                factors.append("Existing stock and open POs already cover the target; buying more would overstock.")
        else:
            best = None
            notes = []
            for s in sups:
                if not s["eligible"]:
                    notes.append(f"{s['supplier_id']} skipped: reliability {s['reliability']} below policy.")
                    continue
                calc = tools.call("calculate_replenishment", sku=sku, node=node,
                                  lead_time_days=s["lead_time_days"], incoming_override=incoming)
                need = calc["need_qty"]
                if need <= 0:
                    continue
                desired = max(ceil_pack(need, s["pack_size"]), s["moq"])
                afford = budget_cents // cents(s["unit_price"])
                limits = {"supplier stock": s["available_qty"], "budget": afford, "storage": storage_free}
                cap_raw = min(limits.values())
                deliver = floor_pack(min(desired, cap_raw), s["pack_size"])
                if deliver < s["moq"]:
                    notes.append(f"{s['supplier_id']} cannot deliver at least its MOQ {s['moq']} "
                                 f"(limits: {limits}).")
                    continue
                if position + deliver > calc["max_cover_qty"]:
                    notes.append(f"{s['supplier_id']} would overshoot the stock ceiling.")
                    continue
                binding = min(limits, key=limits.get) if cap_raw < desired else None
                cand = {"s": s, "calc": calc, "need": need, "deliver": deliver, "cap_raw": cap_raw, "binding": binding}
                key = (deliver, s["supplier_id"] == preferred, -cents(s["unit_price"]), s["reliability"])
                if best is None or key > best[0]:
                    best = (key, cand)
            factors += notes
            if best is None:
                decision = "escalate"
                escalation = {"reason": f"{base['need_qty']} units are needed but no eligible supplier can deliver within budget, "
                                        f"storage and stock limits.",
                              "follow_up": "Buyer to find a new source, raise budget, or transfer stock from another node."}
            else:
                c = best[1]
                s, qty = c["s"], c["deliver"]
                rec = case.get("recommended_qty")
                if (rec and s["supplier_id"] == preferred and abs(rec - c["need"]) / c["need"] <= policy.accept_tolerance
                        and rec % s["pack_size"] == 0 and s["moq"] <= rec <= c["cap_raw"]
                        and position + rec <= c["calc"]["max_cover_qty"]):
                    qty = rec
                actions.append({"action": "create_po", "sku": sku, "node": node,
                                "supplier_id": s["supplier_id"], "qty": qty})
                factors.append(f"Supplier {s['supplier_id']} ({s['name']}) chosen: ${s['unit_price']:.2f}/unit, "
                               f"lead {s['lead_time_days']}d, can ship {s['available_qty']}.")
                shortfall = max(0, c["need"] - qty)
                if shortfall:
                    factors.append(f"Constraint binding: {c['binding']}. Can only buy {qty} of {c['need']} needed.")
                    escalation = {"reason": f"Short by {shortfall} units ({c['binding']} limit). Buying {qty} now.",
                                  "follow_up": f"Approve about ${shortfall * s['unit_price']:.2f} extra budget or free storage to buy the remaining {shortfall}."
                                  if c["binding"] != "supplier stock" else "Find another supplier for the remainder."}
                if rec and not any(x["action"] == "amend_po" for x in actions) and qty == rec:
                    decision = "accept"
                else:
                    decision = "modify"
                if a["status"] == "sustained_surge":
                    cover = inv["on_hand"] / a["effective_daily"]
                    eta = min((p["eta_days"] for p in pos), default=None)
                    if eta is not None and cover < eta:
                        factors.append(f"Warning: on-hand stock lasts about {cover:.1f} days, the open PO lands in {eta}; short-term stock-out is likely.")

        rationale = {
            "accept": "The recommendation matches the real need and respects every constraint, so it is accepted.",
            "modify": "The recommendation or open orders need to change; the adjusted plan below fits demand and constraints.",
            "reject": "The recommendation is not needed; existing stock and open orders already cover demand.",
            "investigate": "Evidence is not strong enough to change the purchasing plan; the buyer should check first.",
            "escalate": "The need is real but cannot be met automatically; a buyer must decide.",
        }[decision]
        if case.get("recommended_qty") and decision != "accept":
            rationale += f" Original recommendation was {case['recommended_qty']} units."
        return {"decision": decision, "rationale": rationale, "factors": factors,
                "actions": actions, "escalation": escalation}
