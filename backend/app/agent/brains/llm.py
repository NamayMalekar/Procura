"""LLM brain: Claude investigates with the same read-only tools, then submits a proposal.
The validator still checks everything, so a wrong LLM answer cannot reach the suppliers."""
import json
from app.agent.tools import TOOL_SPECS
from app.core.config import settings
from app.core.exceptions import BrainError

SYSTEM = """You are an AI purchasing agent helping a retail / quick-commerce buyer.
You receive a case (a purchase recommendation, a supplier shortfall, or a demand alert).
The recommendation you are given is NOT necessarily correct. Investigate with the tools first:
inventory, demand (check whether a surge is sustained or a one-day spike), open POs, supplier options, budget.
Policy:
- Target stock = effective daily demand x (supplier lead time + review period) + safety stock. Use calculate_replenishment.
- Never exceed budget, storage capacity, supplier stock, or order below MOQ. Quantities must be multiples of pack size.
- Do not use suppliers with eligible=false.
- If a PO has supplier_shortfall=true, amend it to effective_qty (action amend_po) and re-plan the gap.
- If a constraint stops you buying the full need, buy what you can AND add an escalation explaining the gap.
- If evidence is weak, decide 'investigate' with an escalation note and no orders.
- Decisions: accept | modify | reject | investigate | escalate.
When ready, call submit_proposal exactly once."""

SUBMIT = {
    "name": "submit_proposal",
    "description": "Submit the final decision. Actions are executed only after validation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "decision": {"type": "string", "enum": ["accept", "modify", "reject", "investigate", "escalate"]},
            "rationale": {"type": "string"},
            "factors": {"type": "array", "items": {"type": "string"}},
            "actions": {"type": "array", "items": {"type": "object", "properties": {
                "action": {"type": "string", "enum": ["create_po", "amend_po", "cancel_po"]},
                "sku": {"type": "string"}, "node": {"type": "string"}, "supplier_id": {"type": "string"},
                "qty": {"type": "integer"}, "po_id": {"type": "string"}}, "required": ["action"]}},
            "escalation": {"type": "object", "properties": {"reason": {"type": "string"}, "follow_up": {"type": "string"}}},
        },
        "required": ["decision", "rationale", "actions"],
    },
}


class LLMBrain:
    name = "llm"

    def __init__(self):
        if not settings.anthropic_api_key:
            raise BrainError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def propose(self, case, tools, feedback=None):
        msgs = [{"role": "user", "content": json.dumps({"case": case, "feedback_from_last_attempt": feedback}, indent=2)}]
        for _ in range(settings.llm_max_turns):
            resp = self.client.messages.create(model=settings.llm_model, max_tokens=2000, system=SYSTEM,
                                               tools=TOOL_SPECS + [SUBMIT], messages=msgs)
            msgs.append({"role": "assistant", "content": resp.content})
            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    if b.name == "submit_proposal":
                        p = dict(b.input)
                        p.setdefault("factors", [])
                        p.setdefault("escalation", None)
                        return p
                    results.append({"type": "tool_result", "tool_use_id": b.id,
                                    "content": json.dumps(tools.call(b.name, **b.input))})
            msgs.append({"role": "user", "content": results or "Call submit_proposal with your final decision."})
        raise BrainError("LLM did not submit a proposal")
