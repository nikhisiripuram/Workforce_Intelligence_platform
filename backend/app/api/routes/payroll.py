from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import csv
import io

from backend.app.models.employee import Employee
from backend.app.services.metrics_service import generate_employee_metrics
from backend.app.services.payroll_service import get_employee_payslip
from backend.app.services.payroll_ai_service import explain_payroll_run
from backend.app.db.session import get_db
from backend.app.services.payroll_service import (
    PayrollExecutionError,
    get_payroll_run_summary,
    get_payroll_run_entries,
    run_payroll,
    get_consolidated_payroll,
)

router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.post("/run")
def execute_payroll(
    run_month: str,
    executed_by: str,
    db: Session = Depends(get_db),
):
    try:
        run_id = run_payroll(db, run_month, executed_by)
        return {
            "status": "success",
            "payroll_run_id": run_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/metrics/run")
def run_metrics(run_month: str, db: Session = Depends(get_db)):
    generate_employee_metrics(db, run_month)
    return {"status": "metrics generated"}

@router.get("/run/{run_id}/summary")
def payroll_run_summary(
    run_id: int,
    db: Session = Depends(get_db),
):
    result = get_payroll_run_summary(db=db, run_id=run_id)

    if not result:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    return result


@router.get("/run/{run_id}/entries")
def payroll_run_entries(
    run_id: int,
    db: Session = Depends(get_db),
):
    results = get_payroll_run_entries(db=db, run_id=run_id)

    if not results:
        raise HTTPException(status_code=404, detail="No payroll entries found")

    return results


@router.get("/run/{run_id}/consolidated")
def consolidated_payroll(
    run_id: int,
    db: Session = Depends(get_db),
):
    data = get_consolidated_payroll(db, run_id)  # <-- fixed argument order

    if not data:
        raise HTTPException(status_code=404, detail="No payroll data found")

    return data

@router.get("/run/{run_id}/explain")
def explain_payroll(
    run_id: int,
    db: Session = Depends(get_db),
):
    explanation = explain_payroll_run(db, run_id)
    return {
        "run_id": run_id,
        "explanation": explanation
    }


@router.get("/run/{run_id}/employee/{employee_id}/payslip")
def employee_payslip(
    run_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
):
    data = get_employee_payslip(db, run_id, employee_id)

    if not data:
        raise HTTPException(status_code=404, detail="Payslip not found")

    explanation = (
        f"Payslip for {data['employee_name']} for {data['run_month']}. "
        f"Gross pay is {data['gross_pay']}. "
        f"Net pay after deductions is {data['net_pay']}."
    )

    return {
        "run_id": run_id,
        "employee_id": employee_id,
        "explanation": explanation,
        **data,
    }

@router.post("/run")
def run_payroll_api(
    run_month: str,
    executed_by: str,
    db: Session = Depends(get_db),
):
    try:
        payroll_run_id = run_payroll(
            db=db,
            run_month=run_month,
            executed_by=executed_by,
        )
        return {
            "status": "success",
            "payroll_run_id": payroll_run_id,
        }

    except PayrollExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
