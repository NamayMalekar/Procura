"""Scorecard. Golden answers are written by hand (not computed by the agent's own code),
and constraints are re-checked against the FINAL store, independent of the validator."""
from .agent import Agent
from .brain_rules import RulesBrain
from .data import CASES
from .store import Store
from .validator import EVIDENCE

# decision, units bought in total, which supplier(s), PO amendments, escalation, cycles, final status
EXPECT = {
    "S1a": dict(decision="accept", new_qty=800, suppliers={"SUP-1"}, status="completed"),
    "S1b": dict(decision="reject", new_qty=0, status="no_action"),
    "S1c": dict(decision="modify", new_qty=600, suppliers={"SUP-9"}, status="completed"),
    "S1d": dict(decision="reject", new_qty=0, status="no_action"),
    "S2a": dict(decision="modify", new_qty=290, suppliers={"SUP-3"}, amends={"PO-9001": 250}, status="completed"),
    "S2b": dict(decision="modify", new_qty=0, amends={"PO-9002": 250}, status="completed"),
    "S3a": dict(decision="modify", new_qty=480, suppliers={"SUP-5"}, status="completed"),
    "S3b": dict(decision="investigate", new_qty=0, escalated=True, status="escalated"),
    "S4a": dict(decision="modify", new_qty=500, suppliers={"SUP-6"}, escalated=True, status="completed_with_escalation"),
    "S4b": dict(decision="accept", new_qty=560, suppliers={"SUP-8"}, min_cycles=2, status="completed"),
}


def agent_pos(store, sku):
    return [p for p in store.s["pos"].values() if p["created_by"] == "agent" and p["sku"] == sku
            and p["status"] in ("confirmed", "partial")]


def evaluate(case, run, store, exp):
    checks = []

    def chk(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    sku, node = case["sku"], case["node"]
    pos = agent_pos(store, sku)
    bought = sum(store.po_qty(p) for p in pos)
    last = run["cycles"][-1]

    chk("decision_correct", run["decision"] == exp["decision"], f"got '{run['decision']}', expected '{exp['decision']}'")
    used = {t["tool"] for t in last["tool_calls"]}
    miss = EVIDENCE[case["type"]] - used
    chk("got_necessary_information", not miss, "all required tools used" if not miss else f"missing {sorted(miss)}")
    inv = store.inventory(sku, node)
    pos_final = inv["on_hand"] + store.incoming(sku, node)
    ok_c = store.budget(sku)["remaining"] >= 0 and all(p["qty"] % store.supplier_item(p["supplier_id"], sku)["pack_size"] == 0 for p in pos)
    started_over = pos_final - bought > inv["storage_capacity"]
    ok_c = ok_c and (pos_final <= inv["storage_capacity"] or started_over)
    chk("respected_constraints", ok_c, f"budget left {store.budget(sku)['remaining']:.2f}, stock position {pos_final}/{inv['storage_capacity']}")
    ok_a = bought == exp["new_qty"] and {p["supplier_id"] for p in pos} == exp.get("suppliers", set())
    for pid, q in exp.get("amends", {}).items():
        ok_a = ok_a and store.po(pid)["qty"] == q
    ok_a = ok_a and (bool(run.get("ticket")) == exp.get("escalated", False))
    chk("took_appropriate_action", ok_a, f"bought {bought}, expected {exp['new_qty']}; suppliers {sorted({p['supplier_id'] for p in pos})}")
    ver = last.get("verification")
    chk("validated_result", bool(ver and ver["ok"]), "verification passed" if ver and ver["ok"] else "verification failed")
    if "min_cycles" in exp:
        chk("recovered_from_failure", len(run["cycles"]) >= exp["min_cycles"] and run["status"].startswith("completed"),
            f"{len(run['cycles'])} cycles, final status {run['status']}")
    chk("final_status", run["status"] == exp["status"], f"got '{run['status']}', expected '{exp['status']}'")
    return checks


def evaluate_all(brain_factory=RulesBrain):
    out = []
    for case in CASES:
        store = Store()
        run = Agent(store, brain_factory(), auto_approve=True).run(case)
        checks = evaluate(case, run, store, EXPECT[case["id"]])
        out.append({"case": case, "status": run["status"], "decision": run["decision"],
                    "cycles": len(run["cycles"]), "checks": checks, "pass": all(c["pass"] for c in checks)})
    return {"results": out, "passed": sum(r["pass"] for r in out), "total": len(out)}
