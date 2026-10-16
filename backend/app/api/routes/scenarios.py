from fastapi import APIRouter
from app.evaluation.cases import CASES

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios")
def scenarios():
    return CASES
