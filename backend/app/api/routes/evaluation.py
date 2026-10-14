from fastapi import APIRouter

from app.evaluation.metrics import load_evaluation_summary

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/summary")
def evaluation_summary() -> dict:
    return load_evaluation_summary()
