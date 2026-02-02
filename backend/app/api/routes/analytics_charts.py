from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.charts_service import (
    department_efficiency_chart,
    peer_distribution_chart,
    salary_vs_efficiency_chart,
    employee_efficiency_trend,
)

router = APIRouter(prefix="/analytics/charts", tags=["Analytics Charts"])

@router.get("/department-efficiency")
def department_efficiency(
    run_month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    return {
        "run_month": run_month,
        "data": department_efficiency_chart(db, run_month),
    }

@router.get("/peer-distribution")
def peer_distribution(
    run_month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    return {
        "run_month": run_month,
        "buckets": peer_distribution_chart(db, run_month),
    }

@router.get("/salary-vs-efficiency")
def salary_efficiency(
    run_month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
):
    return {
        "run_month": run_month,
        "points": salary_vs_efficiency_chart(db, run_month),
    }

@router.get("/employee-trend/{employee_id}")
def employee_trend(
    employee_id: int,
    db: Session = Depends(get_db),
):
    return {
        "employee_id": employee_id,
        "trend": employee_efficiency_trend(db, employee_id),
    }
