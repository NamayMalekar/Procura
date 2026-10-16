"""A 'brain' turns a case into a proposal. Two are provided; both use the same tools."""
from app.core.config import settings
from .rules import RulesBrain


def make_brain(kind=None):
    kind = kind or settings.agent_brain
    if kind == "rules":
        return RulesBrain()
    from .llm import LLMBrain
    if kind == "llm":
        return LLMBrain()
    try:                                   # "auto": Claude if a key exists, otherwise built-in rules
        return LLMBrain() if settings.anthropic_api_key else RulesBrain()
    except Exception:
        return RulesBrain()
