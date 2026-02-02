from sqlalchemy.orm import Session

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric


def get_cost_efficiency_scatter(
    db: Session,
    run_month: str
):
    rows = (
        db.query(
            Employee.id.label("employee_id"),
            Employee.name,
            Employee.department,
            EmployeeMetric.hourly_rate,
            EmployeeMetric.efficiency_score,
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(EmployeeMetric.run_month == run_month)
        .all()
    )

    if not rows:
        raise ValueError("No metrics found for this run_month")

    points = []
    for r in rows:
        points.append({
            "employee_id": r.employee_id,
            "name": r.name,
            "department": r.department,
            "hourly_rate": round(r.hourly_rate, 2),
            "efficiency_score": round(r.efficiency_score, 2),
        })

    return {
        "run_month": run_month,
        "total_employees": len(points),
        "points": points
    }
