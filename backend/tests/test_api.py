from fastapi.testclient import TestClient
from app.main import create_app


def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "api.db")))


def test_api_end_to_end(tmp_path):
    c = client(tmp_path)
    assert c.get("/api/health").json()["status"] == "ok"
    assert len(c.get("/api/scenarios").json()) == 10
    r = c.post("/api/runs", json={"case_id": "S1c", "brain": "rules", "auto_approve": True}).json()
    assert r["status"] == "completed" and r["decision"] == "modify"
    st = c.get("/api/state").json()
    assert any(p["created_by"] == "agent" and p["qty"] == 600 for p in st["purchase_orders"])
    assert c.get("/api/runs").json()[0]["case_id"] == "S1c"
    assert c.get("/api/evaluation").json()["passed"] == 10


def test_approval_flow_over_api(tmp_path, monkeypatch):
    from app.core.policy import policy
    monkeypatch.setattr(policy, "approval_threshold", 500)
    c = client(tmp_path)
    r = c.post("/api/runs", json={"case_id": "S1a", "brain": "rules"}).json()
    assert r["status"] == "pending_approval"
    done = c.post(f"/api/runs/{r['run_id']}/approval", json={"approve": True}).json()
    assert done["status"] == "completed"
    assert c.post(f"/api/runs/{r['run_id']}/approval", json={"approve": True}).status_code == 400


def test_reset_and_unknown_case(tmp_path):
    c = client(tmp_path)
    assert c.post("/api/runs", json={"case_id": "nope"}).status_code == 404
    c.post("/api/runs", json={"case_id": "S1c", "brain": "rules", "auto_approve": True})
    c.post("/api/system/reset")
    assert not [p for p in c.get("/api/state").json()["purchase_orders"] if p["created_by"] == "agent"]
