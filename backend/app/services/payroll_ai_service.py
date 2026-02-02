from sqlalchemy.orm import Session
from backend.app.services.payroll_service import get_payroll_run_summary
from openai import OpenAI

client = OpenAI()

def explain_payroll_run(db: Session, run_id: int) -> str:
    summary = get_payroll_run_summary(db, run_id)

    if not summary:
        return "Payroll run not found."

    prompt = f"""
You are a payroll analyst.

Explain the following payroll run in simple business language:

Month: {summary['run_month']}
Status: {summary['status']}
Employees paid: {summary['total_employees']}
Total gross payout: {summary['total_gross']}
Total net payout: {summary['total_net']}
Average risk score: {summary['avg_risk_score']}

Keep it concise and professional.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content
    