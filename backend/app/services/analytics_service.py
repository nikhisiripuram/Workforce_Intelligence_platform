from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric


def get_employee_comparison(
    db: Session,
    employee_id: int,
    run_month: str,
):
    metric = (
        db.query(EmployeeMetric)
        .filter(
            EmployeeMetric.employee_id == employee_id,
            EmployeeMetric.run_month == run_month,
        )
        .first()
    )

    if not metric:
        return None

    # get employee details explicitly
    emp = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )
    if not emp:
        return None
    department = emp.department

    dept_avg = (
        db.query(func.avg(EmployeeMetric.efficiency_score))
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(
            Employee.department == department,
            EmployeeMetric.run_month == run_month,
        )
        .scalar()
    )

    return {
        "employee_id": employee_id,
        "name": emp.name,
        "role": emp.job_title,
        "department": emp.department,
        "hourly_rate": metric.hourly_rate,
        "peer_percentile": metric.peer_percentile,
        "efficiency_score": metric.efficiency_score,
        "department_avg_efficiency": round(dept_avg, 2) if dept_avg else 0,
    }


def get_department_performance(db: Session, run_month: str):
    rows = (
        db.query(
            Employee.department,
            func.avg(EmployeeMetric.efficiency_score).label("avg_efficiency"),
            func.avg(EmployeeMetric.hourly_rate).label("avg_hourly"),
            func.count(EmployeeMetric.id).label("employee_count"),
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(EmployeeMetric.run_month == run_month)
        .group_by(Employee.department)
        .all()
    )

    return [
        {
            "department": r.department,
            "avg_efficiency": round(r.avg_efficiency, 2),
            "avg_hourly_rate": round(r.avg_hourly, 2),
            "employee_count": r.employee_count,
        }
        for r in rows
    ]


def get_leaderboard(db: Session, run_month: str, limit: int):
    rows = (
        db.query(
            Employee.name,
            Employee.department,
            EmployeeMetric.efficiency_score,
            EmployeeMetric.peer_percentile,
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(EmployeeMetric.run_month == run_month)
        .order_by(desc(EmployeeMetric.peer_percentile))
        .limit(limit)
        .all()
    )

    return [
        {
            "name": r.name,
            "department": r.department,
            "efficiency_score": r.efficiency_score,
            "peer_percentile": r.peer_percentile,
        }
        for r in rows
    ]
