from fastapi import APIRouter, Depends
from app.api.deps import get_store
from app.core.config import settings
from app.core.policy import policy

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/config")
def config():
    return {"app_name": settings.app_name, "llm_available": bool(settings.anthropic_api_key),
            "model": settings.llm_model, "approval_threshold": policy.approval_threshold}


@router.post("/system/reset")
def reset(store=Depends(get_store)):
    store.reset()
    return {"ok": True}
