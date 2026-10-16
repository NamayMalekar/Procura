from fastapi import APIRouter
from app.evaluation.scorer import evaluate_all

router = APIRouter(tags=["evaluation"])


@router.get("/evaluation")
def evaluation():
    return evaluate_all()
