"""Scorecard. Compares each run with the golden answers, and re-checks constraints on the FINAL
database, independent of the validator."""
from app.agent.agent import Agent
from app.agent.brains.rules import RulesBrain
from app.agent.validator import EVIDENCE
from app.database.store import Store
from .cases import CASES
from .expectations import EXPECT



def agent_pos(store, sku):
    return [p for p in store.all_pos() if p["created_by"] == "agent" and p["sku"] == sku
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
