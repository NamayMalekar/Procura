from fastapi import APIRouter, Depends
from app.api.deps import get_run_service
from app.commons.schemas import ApprovalRequest, RunRequest

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("")
def start_run(req: RunRequest, svc=Depends(get_run_service)):
    return svc.start(req.case_id, req.brain, req.auto_approve)


@router.get("")
def recent_runs(svc=Depends(get_run_service)):
    return svc.recent()


@router.get("/{run_id}")
def get_run(run_id: str, svc=Depends(get_run_service)):
    return svc.get(run_id)


@router.post("/{run_id}/approval")
def decide(run_id: str, req: ApprovalRequest, svc=Depends(get_run_service)):
    return svc.approve(run_id, req.approve)
