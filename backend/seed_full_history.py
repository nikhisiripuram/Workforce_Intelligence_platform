import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

DEPARTMENTS = ["Engineering", "Sales", "Product", "Marketing", "HR"]
NAMES = [
    "Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Ethan Hunt",
    "Fiona Apple", "George Miller", "Hannah Abbott", "Ian Wright", "Jenny Slate",
    "Kevin Hart", "Laura Palmer"
]

def seed_history():
    with engine.connect() as conn:
        print("Cleaning all existing HR data for fresh start...")
        conn.execute(text("DELETE FROM performance_reviews"))
        conn.execute(text("DELETE FROM employee_metrics"))
        conn.execute(text("DELETE FROM payslips"))
        conn.execute(text("DELETE FROM payroll_entries"))
        conn.execute(text("DELETE FROM payroll_runs"))
        conn.execute(text("DELETE FROM run_state"))
        conn.execute(text("UPDATE employees SET manager_id = NULL"))
        conn.execute(text("DELETE FROM employees"))
        conn.commit()

        # Generate 3 years of data
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2026, 2, 1)
        
        current = start_date
        while current <= end_date:
            run_month = current.strftime("%Y-%m")
            year = current.year
            print(f"Generating data for {run_month}...")
            
            # Base salary growth (2-5% per year)
            growth_factor = 1.0 + (year - 2024) * 0.05
            
            # 1. Create Employees for this month
            emp_records = []
            for i, name in enumerate(NAMES):
                dept = DEPARTMENTS[i % len(DEPARTMENTS)]
                # Add some randomness to salaries
                base_salary = ((50000 + (i * 2000)) * growth_factor) * random.uniform(0.95, 1.05)
                email = name.lower().replace(" ", ".") + "@example.com"
                
                res = conn.execute(text("""
                    INSERT INTO employees (run_month, name, email, department, job_title, base_salary, working_hours, is_active, simulate_failure)
                    VALUES (:rm, :n, :e, :d, :j, :s, :h, 1, 0)
                """), {
                    "rm": run_month, "n": name, "e": email, "d": dept, 
                    "j": "Staff" if i > 2 else "Lead", "s": base_salary, "h": 160
                })
                # For MySQL/SQLite, we can use LAST_INSERT_ID or just fetch the one we just made
                eid = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
                emp_records.append({"id": eid, "email": email, "name": name, "department": dept, "base_salary": base_salary})

            # 2. Build Hierarchy within this month
            conn.execute(text("UPDATE employees SET position_level = 'Top', job_title = 'CEO' WHERE id = :id"), {"id": emp_records[0]["id"]})
            conn.execute(text("UPDATE employees SET manager_id = :mid, position_level = 'Senior' WHERE id = :id"), {"mid": emp_records[0]["id"], "id": emp_records[1]["id"]})
            conn.execute(text("UPDATE employees SET manager_id = :mid, position_level = 'Senior' WHERE id = :id"), {"mid": emp_records[0]["id"], "id": emp_records[2]["id"]})
            
            for i in range(3, len(emp_records)):
                mid = emp_records[1]["id"] if i % 2 == 0 else emp_records[2]["id"]
                conn.execute(text("UPDATE employees SET manager_id = :mid, position_level = 'Junior' WHERE id = :id"), {"mid": mid, "id": emp_records[i]["id"]})

            # 3. Metrics with VARIATION
            # Calc department averages for this month
            dept_avgs = {}
            for dept in DEPARTMENTS:
                dept_salaries = [e["base_salary"] for e in emp_records if e["department"] == dept]
                avg_salary = sum(dept_salaries) / len(dept_salaries) if dept_salaries else 50000
                dept_avgs[dept] = avg_salary / 160 # avg hourly

            for i, rec in enumerate(emp_records):
                # Random efficiency between 0.6 and 1.2
                eff = round(random.uniform(0.65, 1.15), 2)
                hourly_rate = (50000 / 160) * growth_factor * random.uniform(0.9, 1.1)
                
                conn.execute(text("""
                    INSERT INTO employee_metrics (employee_id, run_month, hourly_rate, dept_avg_hourly, peer_percentile, efficiency_score)
                    VALUES (:eid, :rm, :hr, :da, :pp, :eff)
                """), {
                    "eid": rec["id"], "rm": run_month, "hr": hourly_rate, "da": dept_avgs[DEPARTMENTS[i%len(DEPARTMENTS)]], "pp": random.randint(10, 90), "eff": eff
                })

            # 4. Mark State Ready
            conn.execute(text("""
                INSERT INTO run_state (run_month, csv_uploaded, payroll_done, metrics_done)
                VALUES (:rm, 1, 1, 1)
            """), {"rm": run_month})

            # Advance 1 month
            next_month = current.month + 1
            next_year = current.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            current = datetime(next_year, next_month, 1)

        conn.commit()
        print("Historical seeding complete.")

if __name__ == "__main__":
    seed_history()
