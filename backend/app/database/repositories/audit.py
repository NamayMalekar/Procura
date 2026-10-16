import json
from ._base import Repo


class AuditRepo(Repo):
    """Append-only log of everything that changed purchase orders."""

    def add(self, event, **payload):
        self.run("INSERT INTO audit_log (event, payload) VALUES (?,?)", (event, json.dumps(payload)))

    def all(self):
        return [{"event": r["event"], **json.loads(r["payload"] or "{}")}
                for r in self.many("SELECT * FROM audit_log ORDER BY id")]
