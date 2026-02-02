import csv
from io import StringIO

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.services.run_state_service import mark_csv_uploaded, mark_payroll_done, mark_metrics_done
from backend.app.services.payroll_service import run_payroll
from backend.app.services.metrics_service import generate_employee_metrics

from backend.app.db.session import get_db
from backend.app.models.employee import Employee


router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.post("/upload")
def upload_payroll_csv_for_run(
    run_month: str = Query(..., description="Payroll run month YYYY-MM"),
    executed_by: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV file required")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))

    inserted = 0

    for row in reader:
        email = row["email"].strip().lower()

        employee = (
            db.query(Employee)
            .filter(
                Employee.email == email,
                Employee.run_month == run_month,
            )
            .first()
        )

        if not employee:
            employee = Employee(
                email=email,
                run_month=run_month,
                is_active=True,          #  REQUIRED
                simulate_failure=False,  # explicit
            )
            db.add(employee)

        employee.name = row["name"].strip()
        employee.department = row["department"].strip()
        employee.base_salary = float(row["base_salary"])
        employee.working_hours = float(row.get("working_hours", 160))

        inserted += 1

    db.commit()
    # Mark CSV uploaded
    mark_csv_uploaded(db, run_month)
    # Auto-trigger payroll run after successful upload
    run_payroll(db, run_month, executed_by)
    mark_payroll_done(db, run_month)

    # Generate metrics
    generate_employee_metrics(db, run_month)
    mark_metrics_done(db, run_month)

    return {
        "status": "success",
        "run_month": run_month,
        "employees_loaded": inserted,
    }

