"""Web API + serves the UI.  Run:  uvicorn backend.main:app --reload"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .agent import Agent, make_brain
from .data import CASES
from .evaluation import evaluate_all
from .store import Store

app = FastAPI(title="AI Purchasing Agent")
STORE = Store()
RUNS = {}          # run_id -> (run dict, agent)
CASE_BY_ID = {c["id"]: c for c in CASES}


class RunReq(BaseModel):
    case_id: str
    brain: str = "auto"            # rules | llm | auto
    auto_approve: bool = False


class ApproveReq(BaseModel):
    approve: bool


@app.get("/api/config")
def get_config():
    return {"llm_available": bool(config.ANTHROPIC_API_KEY), "approval_threshold": config.APPROVAL_THRESHOLD,
            "model": config.LLM_MODEL}


@app.get("/api/scenarios")
def scenarios():
    return CASES


@app.post("/api/reset")
def reset():
    global STORE
    STORE = Store()
    RUNS.clear()
    return {"ok": True}


@app.get("/api/state")
def state():
    s = STORE.s
    rows = []
    for sku, nodes in s["inventory"].items():
        for node, inv in nodes.items():
            rows.append({"sku": sku, "name": s["products"][sku]["name"], "node": node, "on_hand": inv["on_hand"],
                         "incoming": STORE.incoming(sku, node), "capacity": inv["storage_capacity"]})
    return {"inventory": rows, "pos": list(s["pos"].values()), "budgets": s["budgets"],
            "escalations": s["escalations"], "audit": s["audit"]}


@app.post("/api/run")
def run_case(req: RunReq):
    case = CASE_BY_ID.get(req.case_id)
    if not case:
        raise HTTPException(404, "unknown case")
    try:
        agent = Agent(STORE, make_brain(req.brain), auto_approve=req.auto_approve)
    except Exception as e:
        raise HTTPException(400, f"Cannot start brain '{req.brain}': {e}")
    run = agent.run(case)
    RUNS[run["run_id"]] = (run, agent)
    return run


@app.post("/api/runs/{run_id}/approve")
def approve(run_id: str, req: ApproveReq):
    if run_id not in RUNS:
        raise HTTPException(404, "unknown run")
    run, agent = RUNS[run_id]
    try:
        agent.approve(run, req.approve)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return run


@app.get("/api/eval")
def eval_all():
    return evaluate_all()


FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")
