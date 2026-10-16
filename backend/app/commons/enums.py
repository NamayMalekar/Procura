"""Shared words used across the app, in one place, so nobody mistypes a status string."""


class Decision:
    ACCEPT, MODIFY, REJECT, INVESTIGATE, ESCALATE = "accept", "modify", "reject", "investigate", "escalate"
    ALL = (ACCEPT, MODIFY, REJECT, INVESTIGATE, ESCALATE)


class ActionType:
    CREATE_PO, AMEND_PO, CANCEL_PO = "create_po", "amend_po", "cancel_po"
    ALL = (CREATE_PO, AMEND_PO, CANCEL_PO)


class POStatus:
    PLACED, CONFIRMED, PARTIAL, REJECTED, CANCELLED = "placed", "confirmed", "partial", "rejected", "cancelled"
    OPEN = (PLACED, CONFIRMED, PARTIAL)


class CaseType:
    RECOMMENDATION = "purchase_recommendation"
    SHORTFALL = "supplier_shortfall"
    DEMAND_ALERT = "demand_alert"


class RunStatus:
    COMPLETED = "completed"
    COMPLETED_WITH_ESCALATION = "completed_with_escalation"
    NO_ACTION = "no_action"
    ESCALATED = "escalated"
    PENDING_APPROVAL = "pending_approval"
    REJECTED_BY_HUMAN = "rejected_by_human"
    BLOCKED = "blocked_by_validator"
    FAILED_AFTER_RETRIES = "escalated_after_failure"
    NEEDS_REPLAN = "needs_replan"
    FAILED_VERIFICATION = "failed_verification"
