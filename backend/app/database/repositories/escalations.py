from ._base import Repo


class EscalationRepo(Repo):
    """Tickets the agent raises for a human buyer."""

    def add(self, run_id, sku, node, reason, follow_up):
        n = self.one("SELECT COUNT(*) AS n FROM escalations")["n"] + 1
        t = {"id": f"ESC-{n}", "run_id": run_id, "sku": sku, "node": node, "reason": reason, "follow_up": follow_up}
        self.run("INSERT INTO escalations VALUES (:id,:run_id,:sku,:node,:reason,:follow_up)", t)
        return t

    def all(self):
        return self.many("SELECT * FROM escalations ORDER BY rowid")
