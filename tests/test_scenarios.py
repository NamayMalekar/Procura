"""Run with:  pytest -q
Part 1: every scenario against golden answers.
Part 2: the safety net - what happens when the brain is WRONG or the world misbehaves."""
import pytest
from backend import config
from backend.agent import Agent
from backend.brain_rules import RulesBrain
from backend.data import CASES
from backend.evaluation import EXPECT, evaluate
from backend.store import Store

BY_ID = {c["id"]: c for c in CASES}


# ---------------- Part 1: scenarios ----------------
@pytest.mark.parametrize("cid", list(EXPECT))
def test_scenario(cid):
    store = Store()
    run = Agent(store, RulesBrain(), auto_approve=True).run(BY_ID[cid])
    failed = [c for c in evaluate(BY_ID[cid], run, store, EXPECT[cid]) if not c["pass"]]
    assert not failed, failed


# ---------------- Part 2: guardrails ----------------
class ScriptedBrain:
    """Returns pre-written proposals in order. Lets us simulate a bad or recovering brain."""
    name = "scripted"

    def __init__(self, *proposals):
        self.proposals, self.i = list(proposals), 0

    def propose(self, case, tools, feedback=None):
        sku, node = case["sku"], case["node"]
        tools.call("get_inventory", sku=sku, node=node)
        tools.call("get_demand", sku=sku, node=node)
        tools.call("get_open_pos", sku=sku, node=node)
        tools.call("get_supplier_options", sku=sku)
        tools.call("get_budget", sku=sku)
        p = self.proposals[min(self.i, len(self.proposals) - 1)]
        self.i += 1
        return p


def accept_blindly(case):
    return {"decision": "accept", "rationale": "System said so.", "factors": [], "escalation": None,
            "actions": [{"action": "create_po", "sku": case["sku"], "node": case["node"],
                         "supplier_id": case["supplier_id"], "qty": case["recommended_qty"]}]}


def test_validator_blocks_a_bad_brain_and_nothing_is_ordered():
    case, store = BY_ID["S1b"], Store()          # open PO already covers demand
    run = Agent(store, ScriptedBrain(accept_blindly(case))).run(case)
    codes = {v["code"] for a in run["cycles"][0]["attempts"] for v in a["verdict"]["violations"]}
    assert run["status"] == "blocked_by_validator" and "OVERSTOCK" in codes
    assert not [p for p in store.s["pos"].values() if p["created_by"] == "agent"]
    assert run["ticket"]  # buyer is told


def test_brain_can_fix_itself_using_validator_feedback():
    case, store = BY_ID["S1c"], Store()
    good = RulesBrain()
    class Fixer(ScriptedBrain):
        def propose(self, case, tools, feedback=None):
            return super().propose(case, tools, feedback) if feedback is None else good.propose(case, tools, feedback)
    run = Agent(store, Fixer(accept_blindly(case)), auto_approve=True).run(case)
    assert len(run["cycles"][0]["attempts"]) == 2 and run["status"] == "completed"
    assert sum(p["qty"] for p in store.s["pos"].values() if p["created_by"] == "agent") == 600


def test_decision_without_investigation_is_rejected():
    case, store = BY_ID["S1a"], Store()
    class Lazy:
        name = "lazy"
        def propose(self, case, tools, feedback=None):
            return accept_blindly(case)
    run = Agent(store, Lazy()).run(case)
    codes = {v["code"] for v in run["cycles"][0]["attempts"][0]["verdict"]["violations"]}
    assert "MISSING_EVIDENCE" in codes and run["status"] == "blocked_by_validator"


def test_large_orders_wait_for_human_approval(monkeypatch):
    monkeypatch.setattr(config, "APPROVAL_THRESHOLD", 500)
    store, case = Store(), BY_ID["S1a"]
    agent = Agent(store, RulesBrain())
    run = agent.run(case)
    assert run["status"] == "pending_approval"
    assert not [p for p in store.s["pos"].values() if p["created_by"] == "agent"]
    agent.approve(run, True)
    assert run["status"] == "completed" and run["cycles"][-1]["verification"]["ok"]


def test_human_can_reject_pending_order(monkeypatch):
    monkeypatch.setattr(config, "APPROVAL_THRESHOLD", 500)
    store, agent = Store(), Agent(Store(), RulesBrain())
    run = agent.run(BY_ID["S1a"])
    agent.approve(run, False)
    assert run["status"] == "rejected_by_human"


def test_supplier_rejection_is_detected_and_replanned():
    store, case = Store(), BY_ID["S4b"]
    run = Agent(store, RulesBrain(), auto_approve=True).run(case)
    c1, c2 = run["cycles"][0], run["cycles"][1]
    assert any(i["code"] == "ORDER_REJECTED" for i in c1["verification"]["issues"])
    assert c2["verification"]["ok"]
    assert store.budget("SKU-4002")["remaining"] == 0.0   # 560 x $5.00 after the price change


def test_partial_fill_on_replacement_order_triggers_second_cycle():
    store, case = Store(), BY_ID["S2a"]
    store.supplier_item("SUP-3", "SKU-2001")["inject"] = {"type": "partial_once", "fraction": 0.5}
    run = Agent(store, RulesBrain(), auto_approve=True).run(case)
    assert len(run["cycles"]) == 2 and run["status"] == "completed"
    assert store.inventory("SKU-2001", "NODE-A")["on_hand"] + store.incoming("SKU-2001", "NODE-A") == 650


def test_no_alternate_supplier_escalates_instead_of_guessing():
    store, case = Store(), BY_ID["S2a"]
    store.supplier_item("SUP-3", "SKU-2001")["available_qty"] = 0
    run = Agent(store, RulesBrain(), auto_approve=True).run(case)
    assert run["status"] == "completed_with_escalation"   # PO amended, gap escalated
    assert store.po("PO-9001")["qty"] == 250
    assert not [p for p in store.s["pos"].values() if p["created_by"] == "agent"]
    assert run["ticket"]["sku"] == "SKU-2001"


def test_unreliable_supplier_is_never_used():
    store, case = Store(), BY_ID["S2a"]
    store.supplier_item("SUP-3", "SKU-2001")["available_qty"] = 0
    run = Agent(store, RulesBrain(), auto_approve=True).run(case)
    assert all(p["supplier_id"] != "SUP-4" for p in store.s["pos"].values())
