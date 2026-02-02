from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import false
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.run_state_service import validate_run_ready as check_run_ready_service

# This is a dependency function, not a router
def validate_run_ready(
    run_month: str = Query(..., description="The run month to validate (YYYY-MM)"),
    db: Session = Depends(get_db)
) -> str:
    """
    Dependency that validates if the given run_month is ready for analytics.
    Raises 422 if not ready.
    Returns the run_month string if valid.
    """
    state = check_run_ready_service(db, run_month)
    
    if not state["ready"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Run not ready for analytics",
                "missing": state["missing"],
                "run_month": run_month
            }
        )
    
    return run_month

