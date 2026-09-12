from fastapi import APIRouter
from database.metrics import get_metrics as fetch_metrics

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    """
    Fetch deduplicated financial metrics for dashboard consumption.
    """
    return fetch_metrics()