"""Run:  python -m scripts.demo [CASE_ID ...]   -> readable story of what the agent did."""
import sys
from app.agent.agent import Agent
from app.agent.brains.rules import RulesBrain
from app.database.store import Store
from app.evaluation.cases import CASES


def tell(case):
    store = Store()
    run = Agent(store, RulesBrain(), auto_approve=True).run(case)
    print(f"\n=== {case['id']}  {case['title']} ===\nTrigger: {case['trigger']}")
    for cy in run["cycles"]:
        print(f"\n  Cycle {cy['cycle']}: {len(cy['tool_calls'])} tool calls "
              f"({', '.join(sorted({t['tool'] for t in cy['tool_calls']}))})")
        for a in cy["attempts"]:
            p, v = a["proposal"], a["verdict"]
            print(f"   proposal: {p['decision']} {[(x['action'], x.get('qty'), x.get('supplier_id') or x.get('po_id')) for x in p['actions']]}")
            print(f"   validator: {'passed' if v['ok'] else 'BLOCKED ' + str([x['code'] for x in v['violations']])}")
        for r in cy.get("execution", []):
            print(f"   executed: {r['action']} {r['po_id']} -> {r['status']} {r.get('detail') or ''}")
        ver = cy.get("verification")
        if ver:
            print("   verify: " + ("matches expectation" if ver["ok"] else "DIFFERS: " + "; ".join(i["message"] for i in ver["issues"])))
    print(f"\n  Decision: {run['decision']}  | Final status: {run['status']}\n  Why:")
    for f in run["factors"]:
        print(f"    - {f}")
    if run.get("ticket"):
        print(f"  Buyer ticket {run['ticket']['id']}: {run['ticket']['reason']}")


if __name__ == "__main__":
    ids = sys.argv[1:]
    for c in CASES:
        if not ids or c["id"] in ids:
            tell(c)
