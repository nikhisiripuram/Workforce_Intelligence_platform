from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric


def get_department_trend(
    db: Session,
    department: str
):
    rows = (
        db.query(
            EmployeeMetric.run_month.label("run_month"),
            func.count(EmployeeMetric.employee_id).label("headcount"),
            func.avg(EmployeeMetric.efficiency_score).label("avg_efficiency"),
            func.avg(EmployeeMetric.hourly_rate).label("avg_hourly_rate"),
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(Employee.department == department)
        .group_by(EmployeeMetric.run_month)
        .order_by(EmployeeMetric.run_month)
        .all()
    )

    if not rows:
        raise ValueError("No data found for department")

    trend = []
    prev_eff = None

    for r in rows:
        eff = round(r.avg_efficiency, 2)
        hourly = round(r.avg_hourly_rate, 2)

        delta = (
            round(eff - prev_eff, 2)
            if prev_eff is not None
            else None
        )

        trend.append({
            "run_month": r.run_month,
            "headcount": r.headcount,
            "avg_efficiency": eff,
            "avg_hourly_rate": hourly,
            "efficiency_change": delta
        })

        prev_eff = eff

    # Directional signal
    overall_trend = (
        "IMPROVING" if trend[-1]["avg_efficiency"] > trend[0]["avg_efficiency"]
        else "DECLINING" if trend[-1]["avg_efficiency"] < trend[0]["avg_efficiency"]
        else "STABLE"
    )

    return {
        "department": department,
        "overall_trend": overall_trend,
        "timeline": trend
    }
