"""Golden answers, written by hand (NOT computed by the agent's own code)."""

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
