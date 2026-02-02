import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env from backend directory or parent
load_dotenv('../.env')
load_dotenv('.env')

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found")
    sys.exit(1)

engine = create_engine(db_url)

with engine.connect() as conn:
    print("Dropping performance_reviews table...")
    conn.execute(text("DROP TABLE IF EXISTS performance_reviews"))
    
    # Also check if columns were added to employees partially and try to revert if so
    # to avoid "Duplicate column name" error
    try:
        print("Reverting partial employee table changes...")
        conn.execute(text("ALTER TABLE employees DROP COLUMN IF EXISTS job_title"))
        conn.execute(text("ALTER TABLE employees DROP COLUMN IF EXISTS manager_id"))
        conn.execute(text("ALTER TABLE employees DROP COLUMN IF EXISTS position_level"))
    except Exception as e:
        print(f"Note: Could not drop columns (maybe they don't exist yet): {e}")
        
    conn.commit()
    print("Cleanup complete.")
