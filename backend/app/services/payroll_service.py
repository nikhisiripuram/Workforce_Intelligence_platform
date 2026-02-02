from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from backend.app.api import employees
from backend.app.api import employees
from backend.app.models.payroll import PayrollRun, PayrollEntry
from backend.app.models.payslip import Payslip
from backend.app.models.employee import Employee
from backend.app.models.audit_log import AuditLog
from backend.app.services.metrics_service import generate_employee_metrics
from backend.app.services.payslip_validation import (
    validate_payslip,
    PayslipValidationError,
)


# =========================
# READ QUERIES
# =========================

def get_payroll_run_summary(db: Session, run_id: int):
    row = (
        db.query(
            PayrollRun.id.label("run_id"),
            PayrollRun.run_month,
            PayrollRun.status,
            func.count(PayrollEntry.id).label("total_employees"),
            func.coalesce(func.sum(PayrollEntry.gross_pay), 0).label("total_gross"),
            func.coalesce(func.sum(PayrollEntry.net_pay), 0).label("total_net"),
            func.coalesce(func.avg(PayrollEntry.risk_score), 0).label("avg_risk_score"),
            PayrollRun.created_at,
        )
        .outerjoin(PayrollEntry, PayrollEntry.payroll_run_id == PayrollRun.id)
        .filter(PayrollRun.id == run_id)
        .group_by(PayrollRun.id)
        .first()
    )

    if not row:
        return None

    return {
        "run_id": row.run_id,
        "run_month": row.run_month,
        "status": row.status,
        "total_employees": row.total_employees,
        "total_gross": float(row.total_gross),
        "total_net": float(row.total_net),
        "avg_risk_score": float(row.avg_risk_score),
        "created_at": row.created_at,
    }


def get_payroll_run_entries(db: Session, run_id: int):
    rows = (
        db.query(
            PayrollEntry.id,
            Employee.id.label("employee_id"),
            Employee.name.label("employee_name"),
            PayrollEntry.gross_pay,
            PayrollEntry.net_pay,
            PayrollEntry.risk_score,
        )
        .join(Employee, Employee.id == PayrollEntry.employee_id)
        .filter(PayrollEntry.payroll_run_id == run_id)
        .order_by(Employee.name)
        .all()
    )

    return [
        {
            "entry_id": r.id,
            "employee_id": r.employee_id,
            "employee_name": r.employee_name,
            "gross_pay": float(r.gross_pay),
            "net_pay": float(r.net_pay),
            "risk_score": r.risk_score,
        }
        for r in rows
    ]


# =========================
# PAYROLL EXECUTION
# =========================

class PayrollExecutionError(Exception):
    pass


def run_payroll(db: Session, run_month: str, executed_by: str):
    # 1. Fetch employees snapshot for the month
    employees = (
        db.query(Employee)
        .filter(Employee.run_month == run_month)
        .all()
    )

    if not employees:
        raise ValueError("No employees found for this run_month")

    # 2. Prevent duplicate payroll runs
    existing = (
        db.query(PayrollRun)
        .filter(PayrollRun.run_month == run_month)
        .first()
    )
    if existing:
        raise ValueError("Payroll already executed for this run_month")

    # 3. Create payroll run
    payroll_run = PayrollRun(
        run_month=run_month,
        status="PROCESSING"
    )
    db.add(payroll_run)
    db.flush()  # get payroll_run.id

    failed = 0
    total_gross = 0.0

    # 4. Execute payroll
    for emp in employees:
        try:
            gross = emp.base_salary
            net = gross  # keep simple for now

            entry = PayrollEntry(
                payroll_run_id=payroll_run.id,
                employee_id=emp.id,
                gross_pay=gross,
                net_pay=net,
            )
            db.add(entry)

            payslip = Payslip(
                payslip_number=f"PS-{run_month}-{emp.id}",
                employee_id=emp.id,
                payroll_run_id=payroll_run.id,
                run_month=run_month,
                base_salary=emp.base_salary,
                gross_pay=gross,
                net_pay=net,
                status="ISSUED",
            )
            db.add(payslip)

            total_gross += gross

        except Exception as e:
            failed += 1
            db.add(AuditLog(
                action="PAYROLL_FAILED",
                performed_by=executed_by,
                reference_id=emp.id,
                details=str(e)
            ))

    # 5. Finalize run
    payroll_run.total_amount = total_gross
    payroll_run.status = "COMPLETED_WITH_ERRORS" if failed else "COMPLETED"

    db.add(AuditLog(
        action="PAYROLL_EXECUTED",
        performed_by=executed_by,
        reference_id=payroll_run.id
    ))

    db.commit()

    try:
        generate_employee_metrics(db, run_month)
    except Exception as e:
        print(f"[WARN] Metrics generation failed: {e}")
    
    return payroll_run.id

# =========================
# CONSOLIDATION
# =========================

def get_consolidated_payroll(db: Session, base_run_id: int):
    rows = (
        db.query(
            Employee.id.label("employee_id"),
            Employee.name.label("employee_name"),
            func.sum(PayrollEntry.gross_pay).label("total_gross"),
            func.sum(PayrollEntry.net_pay).label("total_net"),
        )
        .join(PayrollEntry, PayrollEntry.employee_id == Employee.id)
        .join(PayrollRun, PayrollRun.id == PayrollEntry.payroll_run_id)
        .filter(
            (PayrollRun.id == base_run_id)
            | (PayrollRun.parent_run_id == base_run_id)
        )
        .group_by(Employee.id, Employee.name)
        .order_by(Employee.name)
        .all()
    )

    return [
        {
            "employee_id": r.employee_id,
            "employee_name": r.employee_name,
            "total_gross": float(r.total_gross),
            "total_net": float(r.total_net),
        }
        for r in rows
    ]


# =========================
# EMPLOYEE PAYSLIP
# =========================

def get_employee_payslip(db: Session, run_id: int, employee_id: int):
    row = (
        db.query(
            Employee.name.label("employee_name"),
            PayrollRun.run_month,
            PayrollEntry.gross_pay,
            PayrollEntry.net_pay,
            PayrollEntry.risk_score,
        )
        .join(PayrollEntry, PayrollEntry.employee_id == Employee.id)
        .join(PayrollRun, PayrollRun.id == PayrollEntry.payroll_run_id)
        .filter(
            PayrollRun.id == run_id,
            Employee.id == employee_id,
        )
        .first()
    )

    if not row:
        return None

    return {
        "employee_name": row.employee_name,
        "run_month": row.run_month,
        "gross_pay": float(row.gross_pay),
        "net_pay": float(row.net_pay),
        "risk_score": row.risk_score,
    }
