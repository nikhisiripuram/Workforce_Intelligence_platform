from backend.app.db.session import SessionLocal
from backend.app.services.payroll_service import run_payroll

def main():
    db = SessionLocal()
    try:
        run_payroll(
            db=db,
            run_month="2026-01",
            executed_by="test-user"
        )
    except Exception as e:
        print("ERROR OCCURRED:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
