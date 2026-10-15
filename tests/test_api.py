from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app)


def test_api_end_to_end():
    c.post("/api/reset")
    assert len(c.get("/api/scenarios").json()) == 10
    r = c.post("/api/run", json={"case_id": "S1c", "brain": "rules", "auto_approve": True}).json()
    assert r["status"] == "completed" and r["decision"] == "modify"
    st = c.get("/api/state").json()
    assert any(p["created_by"] == "agent" and p["qty"] == 600 for p in st["pos"])
    assert c.get("/api/eval").json()["passed"] == 10
