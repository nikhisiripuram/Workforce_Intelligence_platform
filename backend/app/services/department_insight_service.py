from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric
from backend.app.services.quadrant_service import classify_employee_quadrants

def get_department_insights(
    db: Session,
    department: str,
    run_month: str
):
    # 1. Base query
    base_q = (
        db.query(EmployeeMetric)
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(
            Employee.department == department,
            EmployeeMetric.run_month == run_month
        )
    )

    total_employees = base_q.count()
    if total_employees == 0:
        raise ValueError("No employees found for department")

    # 2. Aggregates
    aggregates = (
        db.query(
            func.avg(EmployeeMetric.efficiency_score).label("avg_eff"),
            func.avg(EmployeeMetric.hourly_rate).label("avg_hourly")
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(
            Employee.department == department,
            EmployeeMetric.run_month == run_month
        )
        .first()
    )

    avg_eff = round(aggregates.avg_eff, 2)
    avg_hourly = round(aggregates.avg_hourly, 2)

    # 3. Distribution buckets
    top = base_q.filter(EmployeeMetric.peer_percentile >= 75).count()
    mid = base_q.filter(
        EmployeeMetric.peer_percentile.between(40, 74)
    ).count()
    bottom = base_q.filter(EmployeeMetric.peer_percentile < 40).count()

    # 4. Risk detection
    low_eff_count = base_q.filter(
        EmployeeMetric.efficiency_score < avg_eff * 0.85
    ).count()

    risk_level = (
        "HIGH" if low_eff_count / total_employees > 0.3
        else "MEDIUM" if low_eff_count > 0
        else "LOW"
    )

    # 5. Recommendations
    recommendations = []

    if risk_level == "HIGH":
        recommendations.extend([
            "Department-wide performance review",
            "Workload rebalancing",
            "Manager intervention required"
        ])
    elif risk_level == "MEDIUM":
        recommendations.append("Targeted coaching for low performers")
    else:
        recommendations.append("Department operating within healthy range")

    if avg_hourly > avg_eff * 1.2:
        recommendations.append("Cost-efficiency review suggested")

    # 6. Final payload
    return {
        "department": department,
        "run_month": run_month,
        "headcount": total_employees,
        "averages": {
            "efficiency_score": avg_eff,
            "hourly_rate": avg_hourly
        },
        "distribution": {
            "top_performers": top,
            "mid_performers": mid,
            "low_performers": bottom
        },
        "risk_level": risk_level,
        "recommendations": recommendations
    }

def department_quadrant_summary(db: Session, run_month: str):
    try:
        data = classify_employee_quadrants(db, run_month)
    except ValueError:
        return {
            "run_month": run_month,
            "departments": []
        }

    dept_map = defaultdict(lambda: {
        "total": 0,
        "HIGH_VALUE": 0,
        "STAR": 0,
        "OVERPAID": 0,
        "UNDERUTILIZED": 0,
    })

    for emp in data["employees"]:
        dept = emp["department"]
        quadrant = emp["quadrant"]

        dept_map[dept]["total"] += 1
        dept_map[dept][quadrant] += 1

    summary = []

    for dept, counts in dept_map.items():
        total = counts["total"]

        summary.append({
            "department": dept,
            "total_employees": total,
            "quadrants": {
                "HIGH_VALUE": counts["HIGH_VALUE"],
                "STAR": counts["STAR"],
                "OVERPAID": counts["OVERPAID"],
                "UNDERUTILIZED": counts["UNDERUTILIZED"],
            },
            "percentages": {
                "HIGH_VALUE": round(counts["HIGH_VALUE"] / total * 100, 1),
                "STAR": round(counts["STAR"] / total * 100, 1),
                "OVERPAID": round(counts["OVERPAID"] / total * 100, 1),
                "UNDERUTILIZED": round(counts["UNDERUTILIZED"] / total * 100, 1),
            }
        })

    return {
        "run_month": run_month,
        "departments": summary
    }

def generate_department_insights(db: Session, run_month: str):
    summary = department_quadrant_summary(db, run_month)

    insights = []

    for dept in summary["departments"]:
        total = dept["total_employees"]
        q = dept["percentages"]

        dept_insights = []

        if q["STAR"] >= 35:
            dept_insights.append(
                "High concentration of STAR performers indicates strong execution capability."
            )

        if q["HIGH_VALUE"] >= 40:
            dept_insights.append(
                "Team is cost-efficient with a large share of high-value contributors."
            )

        if q["OVERPAID"] >= 20:
            dept_insights.append(
                "Noticeable overpaid segment detected; compensation alignment may be required."
            )

        if q["UNDERUTILIZED"] >= 20:
            dept_insights.append(
                "Significant underutilization suggests workload or management inefficiencies."
            )

        if not dept_insights:
            dept_insights.append(
                "Department shows a balanced distribution without major efficiency or cost risks."
            )

        insights.append({
            "department": dept["department"],
            "headcount": total,
            "insights": dept_insights[:2]  # HARD CAP — no essays
        })

    return {
        "run_month": run_month,
        "department_insights": insights
    }
