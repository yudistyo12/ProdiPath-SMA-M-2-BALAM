from fastapi import APIRouter, Depends

from backend.routes.auth import require_admin
from backend.routes.dashboard import get_dashboard_summary

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/summary", dependencies=[Depends(require_admin)])
def get_analysis_summary():
    return get_dashboard_summary()
