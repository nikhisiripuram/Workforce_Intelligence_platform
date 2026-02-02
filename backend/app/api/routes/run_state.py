from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.run_state import RunState

router = APIRouter(prefix="/runs", tags=["Run State"])

@router.get("/latest")
def latest_ready_run(db: Session = Depends(get_db)):
    state = (
        db.query(RunState)
        .order_by(RunState.run_month.desc())
        .first()
    )

    if not state:
        return {
            "ready": False,
            "missing": ["CSV_UPLOAD", "PAYROLL_RUN", "METRICS"]
        }

    missing = []
    if not state.csv_uploaded:
        missing.append("CSV_UPLOAD")
    if not state.payroll_done:
        missing.append("PAYROLL_RUN")
    if not state.metrics_done:
        missing.append("METRICS")

    return {
        "ready": len(missing) == 0,
        "run_month": state.run_month,
        "missing": missing
    }