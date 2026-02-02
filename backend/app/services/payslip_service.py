from sqlalchemy.orm import Session
from backend.app.models.payroll import PayrollEntry, PayrollRun
from backend.app.models.employee import Employee

def get_payslip(db: Session, run_id: int, employee_id: int):
    row = (
        db.query(
            Employee.name,
            PayrollRun.run_month,
            PayrollEntry.gross_pay,
            PayrollEntry.net_pay,
        )
        .join(PayrollEntry, PayrollEntry.employee_id == Employee.id)
        .join(PayrollRun, PayrollRun.id == PayrollEntry.payroll_run_id)
        .filter(
            PayrollRun.id == run_id,
            Employee.id == employee_id
        )
        .first()
    )

    if not row:
        return None

    return {
        "employee_name": row.name,
        "month": row.run_month,
        "gross_pay": float(row.gross_pay),
        "net_pay": float(row.net_pay),
    }
