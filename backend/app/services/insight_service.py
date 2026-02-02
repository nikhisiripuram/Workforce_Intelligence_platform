from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric


def get_employee_insights(
    db: Session,
    employee_id: int,
    run_month: str
):
    # 1. Fetch metric row
    metric = (
        db.query(EmployeeMetric)
        .filter(
            EmployeeMetric.employee_id == employee_id,
            EmployeeMetric.run_month == run_month
        )
        .first()
    )

    if not metric:
        raise ValueError("Metrics not found for employee")

    # 2. Fetch employee snapshot
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.run_month == run_month
        )
        .first()
    )

    if not employee:
        raise ValueError("Employee not found for run_month")

    # 3. Department aggregates
    dept_stats = (
        db.query(
            func.avg(EmployeeMetric.efficiency_score).label("dept_eff_avg"),
            func.avg(EmployeeMetric.hourly_rate).label("dept_hourly_avg")
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(
            Employee.department == employee.department,
            EmployeeMetric.run_month == run_month
        )
        .first()
    )

    dept_eff_avg = dept_stats.dept_eff_avg or 0
    dept_hourly_avg = dept_stats.dept_hourly_avg or 0

    # 4. Deterministic signals
    efficiency_gap_pct = 0
    if dept_eff_avg and dept_eff_avg > 0:
        efficiency_gap_pct = round(
            ((metric.efficiency_score - dept_eff_avg) / dept_eff_avg) * 100,
            2
        )

    salary_efficiency_mismatch = (
        metric.hourly_rate > dept_hourly_avg
        and metric.efficiency_score < dept_eff_avg
    )

    # 5. Risk classification
    if efficiency_gap_pct < -20:
        risk = "HIGH"
    elif efficiency_gap_pct < -10:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # 6. Recommendations (rule-based)
    recommendations = []

    if risk == "HIGH":
        recommendations.extend([
            "Immediate manager review",
            "Role-fit assessment",
            "Performance improvement plan"
        ])
    elif risk == "MEDIUM":
        recommendations.extend([
            "Skill gap discussion",
            "Workload evaluation"
        ])
    else:
        recommendations.append("Maintain current trajectory")

    if salary_efficiency_mismatch:
        recommendations.append("Compensation vs output review")

    # 7. Final insight payload
    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "role": employee.job_title,
            "department": employee.department
        },
        "run_month": run_month,
        "summary": _build_summary(
            employee.name,
            efficiency_gap_pct,
            metric.peer_percentile
        ),
        "signals": {
            "efficiency_score": metric.efficiency_score,
            "department_avg_efficiency": round(dept_eff_avg, 2),
            "efficiency_gap_pct": efficiency_gap_pct,
            "peer_percentile": metric.peer_percentile,
            "hourly_rate": metric.hourly_rate,
            "department_avg_hourly": round(dept_hourly_avg, 2)
        },
        "risk_flag": risk,
        "recommendations": recommendations
    }


def _build_summary(name: str, gap: float, percentile: float) -> str:
    if gap < -15:
        return (
            f"{name}'s efficiency is significantly below department average "
            f"and ranks in the bottom {100 - int(percentile)}% of peers."
        )
    if gap < -5:
        return (
            f"{name} is slightly below department efficiency norms "
            f"but remains competitive among peers."
        )
    return (
        f"{name} is performing at or above department efficiency benchmarks."
    )
