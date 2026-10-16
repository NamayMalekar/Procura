import json
from ._base import Repo


class RunRepo(Repo):
    """Every agent run is saved, so the UI can show history and approvals can resume later."""

    def save(self, run):
        existing = self.one("SELECT seq FROM agent_runs WHERE run_id=?", (run["run_id"],))
        seq = existing["seq"] if existing else self.one("SELECT COALESCE(MAX(seq),0)+1 AS n FROM agent_runs")["n"]
        self.run("INSERT OR REPLACE INTO agent_runs VALUES (?,?,?,?,?)",
                 (run["run_id"], run["case"]["id"], run["status"], json.dumps(run, default=str), seq))

    def get(self, run_id):
        r = self.one("SELECT payload FROM agent_runs WHERE run_id=?", (run_id,))
        return json.loads(r["payload"]) if r else None

    def recent(self, limit=30):
        return [{"run_id": r["run_id"], "case_id": r["case_id"], "status": r["status"]}
                for r in self.many("SELECT run_id, case_id, status FROM agent_runs ORDER BY seq DESC LIMIT ?", (limit,))]
