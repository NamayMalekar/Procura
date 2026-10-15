"""The agent loop. Brain proposes -> validator checks -> (human approves if big) ->
executor acts -> verifier compares reality with expectation -> re-plan if different."""
import uuid
from . import config
from .brain_rules import RulesBrain, BrainError
from .executor import apply_action
from .tools import ToolBox
from .validator import validate, verify


def make_brain(kind=None):
    kind = kind or config.AGENT_BRAIN
    if kind == "rules":
        return RulesBrain()
    from .brain_llm import LLMBrain
    if kind == "llm":
        return LLMBrain()
    try:  # auto
        return LLMBrain() if config.ANTHROPIC_API_KEY else RulesBrain()
    except Exception:
        return RulesBrain()


class Agent:
    def __init__(self, store, brain=None, auto_approve=False):
        self.store = store
        self.brain = brain or make_brain()
        self.auto_approve = auto_approve

    # ---- public ------------------------------------------------------------
    def run(self, case):
        run = {"run_id": uuid.uuid4().hex[:8], "case": case, "brain": self.brain.name, "status": "running",
               "decision": None, "rationale": None, "factors": [], "actions": [], "escalation": None,
               "cycles": [], "notes": []}
        self._case = case
        feedback = None
        for n in range(1, config.MAX_CYCLES + 1):
            cyc = {"cycle": n, "feedback_in": feedback, "attempts": [], "tool_calls": []}
            run["cycles"].append(cyc)
            tools = ToolBox(self.store)
            proposal = verdict = None
            for attempt in range(1, config.MAX_PROPOSAL_ATTEMPTS + 1):
                proposal = self._propose(case, tools, feedback, run)
                verdict = validate(self.store, case, proposal, tools.called)
                cyc["attempts"].append({"attempt": attempt, "proposal": proposal, "verdict": verdict})
                if verdict["ok"]:
                    break
                feedback = {"validator_violations": verdict["violations"]}
            cyc["tool_calls"] = tools.log
            self._absorb(run, proposal)
            if not verdict["ok"]:
                run["status"] = "blocked_by_validator"
                self._ticket(run, "Agent could not produce a safe proposal: " +
                             "; ".join(x["message"] for x in verdict["violations"]),
                             "Buyer to handle this case manually.")
                return run
            if verdict["requires_approval"] and not self.auto_approve:
                run["status"] = "pending_approval"
                run["pending"] = {"proposal": proposal, "verdict": verdict}
                return run
            ok, issues = self._execute(cyc, proposal, verdict)
            if ok:
                return self._finish(run, proposal)
            feedback = {"execution_issues": issues}
        run["status"] = "escalated_after_failure"
        self._ticket(run, "Execution kept failing verification after retries: " +
                     "; ".join(i["message"] for i in feedback["execution_issues"]),
                     "Buyer to review open POs for this SKU.")
        return run

    def approve(self, run, approve):
        """Human decision on a pending run. We re-validate first because data may have changed."""
        if run["status"] != "pending_approval":
            raise ValueError("run is not waiting for approval")
        if not approve:
            run["status"] = "rejected_by_human"
            return run
        self._case = run["case"]
        cyc, proposal = run["cycles"][-1], run["pending"]["proposal"]
        called = {t["tool"] for t in cyc["tool_calls"]}
        verdict = validate(self.store, run["case"], proposal, called)
        cyc["approval"] = {"approved": True, "revalidation": verdict}
        if not verdict["ok"]:
            run["status"] = "needs_replan"
            return run
        ok, _ = self._execute(cyc, proposal, verdict)
        run.pop("pending", None)
        if ok:
            return self._finish(run, proposal)
        run["status"] = "failed_verification"
        return run

    # ---- internals ---------------------------------------------------------
    def _propose(self, case, tools, feedback, run):
        try:
            return self.brain.propose(case, tools, feedback)
        except Exception as e:
            if self.brain.name == "rules":
                raise
            run["notes"].append(f"LLM brain failed ({type(e).__name__}: {e}); used rules brain instead.")
            return RulesBrain().propose(case, tools, feedback)

    def _execute(self, cyc, proposal, verdict):
        results = []
        for a in proposal["actions"]:
            try:
                results.append(apply_action(self.store, a, live=True))
            except Exception as e:
                results.append({"action": a["action"], "status": "error", "reason": str(e)})
        v = verify(self.store, self._case, proposal, results, verdict["metrics"])
        cyc["execution"], cyc["verification"] = results, v
        return v["ok"], v["issues"]

    def _absorb(self, run, p):
        for k in ("decision", "rationale", "factors", "actions", "escalation"):
            run[k] = p.get(k) or ([] if k in ("factors", "actions") else None)

    def _finish(self, run, proposal):
        if proposal.get("escalation"):
            self._ticket(run, proposal["escalation"]["reason"], proposal["escalation"].get("follow_up", ""))
        acted = bool(proposal["actions"])
        run["status"] = ("completed_with_escalation" if proposal.get("escalation") else "completed") if acted \
            else ("escalated" if proposal.get("escalation") else "no_action")
        run.pop("pending", None)
        return run

    def _ticket(self, run, reason, follow_up):
        t = {"id": f"ESC-{len(self.store.s['escalations']) + 1}", "run_id": run["run_id"],
             "sku": run["case"]["sku"], "node": run["case"]["node"], "reason": reason, "follow_up": follow_up}
        self.store.s["escalations"].append(t)
        run["ticket"] = t


