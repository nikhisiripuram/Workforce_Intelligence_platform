from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True)

    payslip_number = Column(String(50), unique=True, nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)

    run_month = Column(String(7), nullable=False)

    base_salary = Column(Float, nullable=False)
    gross_pay = Column(Float, nullable=False)
    net_pay = Column(Float, nullable=False)

    status = Column(String(20), default="ISSUED", nullable=False)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
