from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.app.db.session import get_db
from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric
from backend.app.models.performance import PerformanceReview
from backend.app.services.analytics_service import (
    get_employee_comparison,
    get_department_performance,
    get_leaderboard,
)
from backend.app.services.cost_efficiency_service import get_cost_efficiency_scatter
from backend.app.services.department_trend_service import get_department_trend
from backend.app.services.insight_service import get_employee_insights
from backend.app.services.department_insight_service import department_quadrant_summary, generate_department_insights, get_department_insights
from backend.app.services.quadrant_service import classify_employee_quadrants
from backend.app.api.dependencies.run_ready import validate_run_ready as require_run_ready

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/employee/{employee_id}")
def employee_analytics(
    employee_id: int,
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):
    return get_employee_comparison(db, employee_id, run_month)


@router.get("/department")
def department_analytics(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):
    return get_department_performance(db, run_month)


@router.get("/leaderboard")
def leaderboard(
    run_month: str = Depends(require_run_ready),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return get_leaderboard(db, run_month, limit)


@router.get("/insights/employee/{employee_id}")
def employee_insights(
    employee_id: int,
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    return get_employee_insights(db, employee_id, run_month)


@router.get("/insights/department/{department}")
def department_insights(
    department: str,
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    return get_department_insights(db, department, run_month)


@router.get("/trends/department/{department}")
def department_trend(
    department: str,
    db: Session = Depends(get_db)
):
    return get_department_trend(db, department)


@router.get("/scatter/cost-efficiency")
def cost_efficiency_scatter(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):
    return get_cost_efficiency_scatter(db, run_month)


@router.get("/quadrants")
def employee_quadrants(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):
    return classify_employee_quadrants(db, run_month)   


@router.get("/departments/quadrants")
def department_quadrants(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):
    return department_quadrant_summary(db, run_month)


@router.get("/departments/insights")
def department_ai_insights(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db),
):  
    return generate_department_insights(db, run_month)


# --- New Advanced Analytics Endpoints ---

@router.get("/insights/monthly")
def get_monthly_insights(year: int, month: int, db: Session = Depends(get_db)):
    # Simple aggregation example
    # In a real app, this would probably aggregate payroll data + performance
    return {
        "period": f"{year}-{month:02d}",
        "summary": "Monthly insights placeholder",
        "total_payroll": 0, # Implement actual logic
        "avg_performance": 0
    }

@router.get("/insights/quarterly")
def get_quarterly_insights(year: int, quarter: int, db: Session = Depends(get_db)):
    reviews = db.query(PerformanceReview).filter(
        PerformanceReview.year == year,
        PerformanceReview.quarter == quarter
    ).all()
    
    avg_rating = 0
    if reviews:
        avg_rating = sum([r.rating for r in reviews if r.rating]) / len(reviews)
        
    return {
        "period": f"{year}-Q{quarter}",
        "review_count": len(reviews),
        "average_rating": avg_rating,
        "completion_rate": "85%" # Placeholder
    }

@router.get("/insights/yearly")
def get_yearly_insights(year: int, db: Session = Depends(get_db)):
    reviews = db.query(PerformanceReview).filter(PerformanceReview.year == year).all()
    
    avg_rating = 0
    if reviews:
        avg_rating = sum([r.rating for r in reviews if r.rating]) / len(reviews)
        
    return {
        "year": year,
        "total_reviews": len(reviews),
        "average_rating": avg_rating,
        "highlights": ["Top Performer: John Doe", "Best Dept: Engineering"]
    }

@router.get("/summary")
def get_dashboard_summary(
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    """
    Returns high-level summary for the selected run_month.
    - Headcount: Number of employees in this run.
    - Total Payroll: Sum of base salaries.
    - Avg Performance: Average efficiency score for this run.
    """
    employees = db.query(Employee).filter(Employee.run_month == run_month).all()
    count = len(employees)
    total_payroll = sum([e.base_salary for e in employees])
    
    avg_efficiency = (
        db.query(func.avg(EmployeeMetric.efficiency_score))
        .filter(EmployeeMetric.run_month == run_month)
        .scalar()
    ) or 0
    
    return {
        "run_month": run_month,
        "headcount": count,
        "total_payroll": round(total_payroll, 2),
        "avg_performance": round(avg_efficiency, 2),
        "status": "Stable" if count > 0 else "N/A"
    }

@router.get("/all-runs")
def get_all_runs(db: Session = Depends(get_db)):
    """Returns list of all available run_months."""
    runs = db.query(Employee.run_month).distinct().order_by(Employee.run_month.desc()).all()
    return [r[0] for r in runs]