from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric

def department_efficiency_chart(db: Session, run_month: str):
    rows = (
        db.query(
            Employee.department,
            func.avg(EmployeeMetric.efficiency_score).label("avg_efficiency")
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(EmployeeMetric.run_month == run_month)
        .group_by(Employee.department)
        .all()
    )

    return [
        {
            "department": dept,
            "avg_efficiency": round(avg_eff, 2)
        }
        for dept, avg_eff in rows
    ]

def peer_distribution_chart(db: Session, run_month: str):
    buckets = [
        (0, 20),
        (21, 40),
        (41, 60),
        (61, 80),
        (81, 100),
    ]

    result = []

    for low, high in buckets:
        count = (
            db.query(func.count(EmployeeMetric.id))
            .filter(
                EmployeeMetric.run_month == run_month,
                EmployeeMetric.peer_percentile.between(low, high)
            )
            .scalar()
        )

        result.append({
            "range": f"{low}-{high}",
            "count": count
        })

    return result

def salary_vs_efficiency_chart(db: Session, run_month: str):
    rows = (
        db.query(
            Employee.id,
            Employee.department,
            Employee.base_salary,
            EmployeeMetric.efficiency_score
        )
        .join(EmployeeMetric, Employee.id == EmployeeMetric.employee_id)
        .filter(EmployeeMetric.run_month == run_month)
        .all()
    )

    return [
        {
            "employee_id": emp_id,
            "department": dept,
            "salary": salary,
            "efficiency": efficiency
        }
        for emp_id, dept, salary, efficiency in rows
    ]

def employee_efficiency_trend(db: Session, employee_id: int):
    rows = (
        db.query(
            EmployeeMetric.run_month,
            EmployeeMetric.efficiency_score
        )
        .filter(EmployeeMetric.employee_id == employee_id)
        .order_by(EmployeeMetric.run_month)
        .all()
    )

    return [
        {
            "run_month": run_month,
            "efficiency": efficiency
        }
        for run_month, efficiency in rows
    ]

