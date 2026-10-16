"""Use-cases the API calls. Sits between the web layer and the agent."""
from app.agent.agent import Agent
from app.agent.brains import make_brain
from app.agent.brains.rules import RulesBrain
from app.core.exceptions import BrainError, InvalidState, NotFound
from app.evaluation.cases import CASES

CASE_BY_ID = {c["id"]: c for c in CASES}


class RunService:
    def __init__(self, store):
        self.store = store

    def start(self, case_id, brain_kind, auto_approve):
        case = CASE_BY_ID.get(case_id)
        if not case:
            raise NotFound(f"unknown case '{case_id}'")
        try:
            brain = make_brain(brain_kind)
        except BrainError as e:
            raise InvalidState(f"Cannot start brain '{brain_kind}': {e}")
        run = Agent(self.store, brain, auto_approve).run(case)
        self.store.runs.save(run)
        return run

    def approve(self, run_id, approve):
        run = self.store.runs.get(run_id)
        if not run:
            raise NotFound("unknown run")
        if run["status"] != "pending_approval":
            raise InvalidState("This run is not waiting for approval.")
        Agent(self.store, RulesBrain()).approve(run, approve)
        self.store.runs.save(run)
        return run

    def get(self, run_id):
        run = self.store.runs.get(run_id)
        if not run:
            raise NotFound("unknown run")
        return run

    def recent(self):
        return self.store.runs.recent()
