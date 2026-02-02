from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.api.dependencies.run_ready import validate_run_ready as require_run_ready
from backend.app.services.ai_snapshot_service import generate_manager_review, generate_individual_feedback
from backend.app.services.ai_department_service import generate_department_brief

router = APIRouter(prefix="/ai", tags=["AI"])


class PayslipRequest(BaseModel):
    employee_name: str
    run_month: str
    gross_pay: float
    net_pay: float
    risk_score: float | None = None

@router.post("/payslip/explain")
def explain_payslip(data: PayslipRequest):
    explanation = (
        f"Payslip for {data.employee_name} for {data.run_month}. "
        f"Gross pay is {data.gross_pay}. "
        f"Net pay after deductions is {data.net_pay}."
    )
    if data.gross_pay != data.net_pay:
        explanation += "The difference is due to deductions such as taxes or benefits."

    if data.risk_score:
        explanation += f" Risk score noted: {data.risk_score}."
        
    return {
        "explanation": explanation
    }

@router.post("/snapshot/manager/{employee_id}")
def manager_snapshot(
    employee_id: int,
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    review = generate_manager_review(db, employee_id, run_month)
    return {"review": review}

@router.post("/snapshot/individual/{employee_id}")
def individual_snapshot(
    employee_id: int,
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    feedback = generate_individual_feedback(db, employee_id, run_month)
    return {"feedback": feedback}

@router.get("/department/brief")
def get_dept_brief(
    department: str = Query(...),
    run_month: str = Depends(require_run_ready),
    db: Session = Depends(get_db)
):
    brief = generate_department_brief(db, department, run_month)
    return {"department": department, "brief": brief}
