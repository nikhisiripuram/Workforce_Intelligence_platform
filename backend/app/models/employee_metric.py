from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from backend.app.db.base import Base


class EmployeeMetric(Base):
    __tablename__ = "employee_metrics"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    run_month = Column(String(7), nullable=False)

    hourly_rate = Column(Float, nullable=False)
    dept_avg_hourly = Column(Float, nullable=False)

    peer_percentile = Column(Float, nullable=False)
    efficiency_score = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("employee_id", "run_month", name="uq_employee_run"),
    )
