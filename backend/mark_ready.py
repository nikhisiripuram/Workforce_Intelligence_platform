import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

def mark_ready():
    with engine.connect() as conn:
        conn.execute(text("REPLACE INTO run_state (run_month, csv_uploaded, payroll_done, metrics_done) VALUES ('2026-02', 1, 1, 1)"))
        conn.commit()
        print("Run month 2026-02 marked as READY.")

if __name__ == "__main__":
    mark_ready()
