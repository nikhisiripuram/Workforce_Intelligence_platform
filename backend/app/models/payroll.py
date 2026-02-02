from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from datetime import datetime
from backend.app.db.base import Base
from sqlalchemy.orm import relationship  # <-- Add this line

class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True)
    run_month = Column(String(7), nullable=False)
    status = Column(String(20), nullable=False)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 🔑 THIS WAS MISSING
    parent_run_id = Column(
        Integer,
        ForeignKey("payroll_runs.id"),
        nullable=True,
    )

    parent_run = relationship(
        "PayrollRun",
        remote_side=[id],
        backref="adjustment_runs",
    )

class PayrollEntry(Base):
    __tablename__ = "payroll_entries"

    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    gross_pay = Column(Float, nullable=False)
    net_pay = Column(Float, nullable=False)
    risk_score = Column(Float)

