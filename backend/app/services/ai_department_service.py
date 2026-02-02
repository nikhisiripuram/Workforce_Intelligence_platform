from sqlalchemy.orm import Session
from sqlalchemy import func
from openai import OpenAI
from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric
from backend.app.services.department_insight_service import department_quadrant_summary

client = OpenAI()

def generate_department_brief(db: Session, department: str, run_month: str) -> str:
    """
    Generates a strategic AI brief for a specific department and month.
    Covers performance scope, areas of lacking, and recommendations.
    """
    # 1. Gather data
    metrics = (
        db.query(
            func.avg(EmployeeMetric.efficiency_score).label("avg_eff"),
            func.avg(EmployeeMetric.hourly_rate).label("avg_cost"),
            func.count(EmployeeMetric.id).label("headcount")
        )
        .join(Employee, Employee.id == EmployeeMetric.employee_id)
        .filter(
            Employee.department == department,
            EmployeeMetric.run_month == run_month
        )
        .first()
    )

    if not metrics or metrics.headcount == 0:
        return "No data available for this department in the selected period."

    # 2. Get distribution summary
    quadrant_data = department_quadrant_summary(db, run_month)
    dept_quads = next((d for d in quadrant_data["departments"] if d["department"] == department), None)
    
    dist_str = ""
    if dept_quads:
        q = dept_quads["percentages"]
        dist_str = f"Talent Mix: {q['STAR']}% Stars, {q['HIGH_VALUE']}% High Value, {q['OVERPAID']}% Overpaid, {q['UNDERUTILIZED']}% Underutilized."

    prompt = f"""
    You are a senior workforce strategist. Analyze the performance data for the {department} department for {run_month}.

    Key Stats:
    - Headcount: {metrics.headcount}
    - Avg Efficiency Score: {round(metrics.avg_eff, 2)}
    - Avg Hourly Cost: ${round(metrics.avg_cost, 2)}
    {dist_str}

    Task:
    Provide a professional, 3-paragraph strategic brief covering:
    1. **Performance Scope**: Overall health and impact of the department.
    2. **Areas of Lacking**: Specific gaps in efficiency, cost alignment, or talent distribution.
    3. **Growth & Optimization**: Actionable strategic advice for the next quarter.

    Tone: Objective, executive-level, and data-driven.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Brief Error: {e}")
        return f"### {department} Strategic Overview\n\nThe {department} department currently maintains a headcount of {metrics.headcount} with an average efficiency of {round(metrics.avg_eff, 2)}. \n\n**Strategic Focus**: Optimization of talent distribution and cost-to-value ratio. Current trends suggest stability with opportunities for growth in upper-percentile performance brackets."
