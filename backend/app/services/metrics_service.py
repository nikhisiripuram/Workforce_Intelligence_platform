from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.app.models.employee import Employee
from backend.app.models.payroll import PayrollEntry
from backend.app.models.employee_metric import EmployeeMetric


def generate_employee_metrics(
    db: Session,
    run_month: str,
):
    """
    Safe, idempotent metrics generation.
    Can be re-run without duplicates.
    """

    # Fetch all employees for this run
    employees = (
        db.query(Employee)
        .filter(Employee.run_month == run_month)
        .all()
    )

    if not employees:
        return

    # Pre-calc department averages
    dept_avg = dict(
        db.query(
            Employee.department,
            func.avg(
                Employee.base_salary / Employee.working_hours
            ),
        )
        .filter(Employee.run_month == run_month)
        .group_by(Employee.department)
        .all()
    )

    # Get hourly rates ordered (for percentile)
    hourly_rates = (
        db.query(
            Employee.id,
            (Employee.base_salary / Employee.working_hours).label("hourly_rate"),
        )
        .filter(Employee.run_month == run_month)
        .order_by("hourly_rate")
        .all()
    )

    rate_rank = {
        emp_id: idx + 1
        for idx, (emp_id, _) in enumerate(hourly_rates)
    }
    total = len(hourly_rates)

    for emp in employees:
        hourly_rate = emp.base_salary / emp.working_hours
        dept_avg_hourly = dept_avg.get(emp.department, hourly_rate)

        percentile = round(
            (rate_rank[emp.id] / total) * 100, 2
        )

        efficiency_score = round(
            hourly_rate / dept_avg_hourly, 2
        )

        existing = (
            db.query(EmployeeMetric)
            .filter(
                EmployeeMetric.employee_id == emp.id,
                EmployeeMetric.run_month == run_month,
            )
            .first()
        )

        if existing:
            continue

        metric = EmployeeMetric(
            employee_id=emp.id,
            run_month=run_month,
            hourly_rate=hourly_rate,
            dept_avg_hourly=dept_avg_hourly,
            peer_percentile=percentile,
            efficiency_score=efficiency_score,
        )

        db.add(metric)

    db.commit()
