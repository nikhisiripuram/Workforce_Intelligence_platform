from sqlalchemy import Column, String, Boolean
from backend.app.db.base import Base

class RunState(Base):
    __tablename__ = "run_state"

    run_month = Column(String(7), primary_key=True)  # YYYY-MM
    csv_uploaded = Column(Boolean, default=False)
    payroll_done = Column(Boolean, default=False)
    metrics_done = Column(Boolean, default=False)
