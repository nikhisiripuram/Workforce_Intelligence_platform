from sqlalchemy.orm import Session
import statistics

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric


def classify_employee_quadrants(db: Session, run_month: str):
    rows = (
        db.query(
            Employee.id,
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
        return {
            "run_month": run_month,
            "cutoffs": {"cost_median": 0, "efficiency_median": 0},
            "employees": []
        }

    hourly_rates = [r.hourly_rate for r in rows]
    efficiency_scores = [r.efficiency_score for r in rows]

    cost_median = statistics.median(hourly_rates)
    efficiency_median = statistics.median(efficiency_scores)

    results = []

    for r in rows:
        if r.hourly_rate <= cost_median and r.efficiency_score >= efficiency_median:
            quadrant = "HIGH_VALUE"
        elif r.hourly_rate > cost_median and r.efficiency_score >= efficiency_median:
            quadrant = "STAR"
        elif r.hourly_rate > cost_median and r.efficiency_score < efficiency_median:
            quadrant = "OVERPAID"
        else:
            quadrant = "UNDERUTILIZED"

        results.append({
            "employee_id": r.id,
            "name": r.name,
            "department": r.department,
            "hourly_rate": round(r.hourly_rate, 2),
            "efficiency_score": round(r.efficiency_score, 2),
            "quadrant": quadrant,
        })

    return {
        "run_month": run_month,
        "cutoffs": {
            "cost_median": round(cost_median, 2),
            "efficiency_median": round(efficiency_median, 2),
        },
        "employees": results,
    }
