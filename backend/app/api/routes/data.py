from fastapi import APIRouter, Depends
from app.api.deps import get_store

router = APIRouter(tags=["data"])


@router.get("/state")
def state(store=Depends(get_store)):
    return store.snapshot()
