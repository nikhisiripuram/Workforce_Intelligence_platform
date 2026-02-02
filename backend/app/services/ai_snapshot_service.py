from sqlalchemy.orm import Session
from openai import OpenAI
from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric
from backend.app.services.quadrant_service import classify_employee_quadrants

client = OpenAI()

def get_employee_data(db: Session, employee_id: int, run_month: str):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    metrics = db.query(EmployeeMetric).filter(
        EmployeeMetric.employee_id == employee_id,
        EmployeeMetric.run_month == run_month
    ).first()

    if not employee or not metrics:
        return None

    # Get quadrant context
    quadrant_data = classify_employee_quadrants(db, run_month)
    emp_quadrant = next(
        (e for e in quadrant_data["employees"] if e["employee_id"] == employee_id),
        None
    )

    return {
        "name": employee.name,
        "role": employee.job_title,
        "department": employee.department,
        "metrics": metrics,
        "quadrant": emp_quadrant["quadrant"] if emp_quadrant else "UNKNOWN"
    }

def generate_manager_review(db: Session, employee_id: int, run_month: str) -> str:
    data = get_employee_data(db, employee_id, run_month)
    if not data:
        return "Employee data not found."

    metrics = data["metrics"]
    
    prompt = f"""
    You are an expert HR and workforce analyst. Write a confidential review for a manager regarding their direct report.

    Employee: {data['name']} ({data['role']}, {data['department']})
    Performance Quadrant: {data['quadrant']}
    
    Key Metrics:
    - Efficiency Score: {metrics.efficiency_score} (Peer Percentile: {metrics.peer_percentile}%)
    - Hourly Cost: ${metrics.hourly_rate}
    - Risk Score: {metrics.risk_score}/100

    Task:
    Provide a concise strategic review (3-4 paragraphs) covering:
    1. **Retention Risk**: Based on risk score and quadrant.
    2. **Value Assessment**: Is the employee delivering value relative to cost?
    3. **Actionable Recommendation**: Targeted advice for the manager (e.g., "Assign higher complexity tasks," "Review compensation," "Provide coaching").

    Tone: Professional, objective, and action-oriented.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content

def generate_individual_feedback(db: Session, employee_id: int, run_month: str) -> str:
    data = get_employee_data(db, employee_id, run_month)
    if not data:
        return "Employee data not found."

    metrics = data["metrics"]
    
    prompt = f"""
    You are a supportive performance coach. Write a constructive feedback summary for the employee to read.

    Employee: {data['name']} ({data['role']})
    
    Performance Data:
    - Efficiency: {metrics.efficiency_score} (Top {100 - metrics.peer_percentile}% of peers)
    - Classification: {data['quadrant']}

    Task:
    Provide a motivating feedback summary (3-4 paragraphs) covering:
    1. **Strengths**: What are they doing well based on the data?
    2. **Growth Opportunities**: Areas to improve efficiency or impact.
    3. **Career Tip**: A generic but relevant tip for someone in their position/quadrant.

    Tone: Encouraging, constructive, and forward-looking. Avoid using internal jargon like "Quadrant" or "Risk Score" directly.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content
