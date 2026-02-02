
from backend.app.models.employee import Employee
from backend.app.models.employee_metric import EmployeeMetric
from sqlalchemy.orm import Session
from backend.app.api.routes.run_state import RunState
from backend.app.models.payroll import PayrollRun



def upsert_run_state(db, run_month, **flags):
    state = db.query(RunState).filter_by(run_month=run_month).first()

    if not state:
        state = RunState(run_month=run_month)
        db.add(state)

    for key, value in flags.items():
        setattr(state, key, value)

    db.commit()
    return state


def mark_csv_uploaded(db, run_month):
    upsert_run_state(db, run_month, csv_uploaded=True)

def mark_payroll_done(db, run_month):
    upsert_run_state(db, run_month, payroll_done=True)

def mark_metrics_done(db, run_month):
    upsert_run_state(db, run_month, metrics_done=True)

def validate_run_ready(db, run_month):
    state = db.query(RunState).filter_by(run_month=run_month).first()

    missing = []

    if not state or not state.csv_uploaded:
        missing.append("CSV_UPLOAD")
    if not state or not state.payroll_done:
        missing.append("PAYROLL_RUN")
    if not state or not state.metrics_done:
        missing.append("METRICS")

    return {
        "ready": len(missing) == 0,
        "missing": missing
    }