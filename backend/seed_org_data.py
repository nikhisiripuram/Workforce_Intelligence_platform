import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('../.env')
load_dotenv('.env')

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    exit(1)

engine = create_engine(db_url)

def seed_org():
    with engine.connect() as conn:
        print("Cleaning up existing employees to reset hierarchy...")
        # We'll just update existing ones if they exist, or keep it simple
        
        # 1. Ensure we have at least 10 employees
        res = conn.execute(text("SELECT id FROM employees LIMIT 10")).fetchall()
        if len(res) < 5:
            print("Not enough employees found. Please upload a payroll CSV first.")
            return

        ids = [r[0] for r in res]
        
        print(f"Setting hierarchy for {len(ids)} employees...")
        
        # CEO / Top
        conn.execute(text("UPDATE employees SET position_level = 'Top', job_title = 'CEO', manager_id = NULL WHERE id = :id"), {"id": ids[0]})
        
        # VPs / Seniors (Reporting to CEO)
        if len(ids) > 1:
            conn.execute(text("UPDATE employees SET position_level = 'Senior', job_title = 'VP Engineering', manager_id = :mid WHERE id = :id"), {"mid": ids[0], "id": ids[1]})
        if len(ids) > 2:
            conn.execute(text("UPDATE employees SET position_level = 'Senior', job_title = 'VP Product', manager_id = :mid WHERE id = :id"), {"mid": ids[0], "id": ids[2]})
            
        # Managers (Reporting to VPs)
        if len(ids) > 3:
            conn.execute(text("UPDATE employees SET position_level = 'Middle', job_title = 'Engineering Manager', manager_id = :mid WHERE id = :id"), {"mid": ids[1], "id": ids[3]})
        if len(ids) > 4:
            conn.execute(text("UPDATE employees SET position_level = 'Middle', job_title = 'Product Manager', manager_id = :mid WHERE id = :id"), {"mid": ids[2], "id": ids[4]})

        # Rest report to someone
        for i in range(5, len(ids)):
            mid = ids[3] if i % 2 == 0 else ids[4]
            conn.execute(text("UPDATE employees SET position_level = 'Junior', job_title = 'Individual Contributor', manager_id = :mid WHERE id = :id"), {"mid": mid, "id": ids[i]})
            
        conn.commit()
        print("Hierarchy seeded successfully.")

if __name__ == "__main__":
    seed_org()
