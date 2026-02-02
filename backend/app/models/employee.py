from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    run_month = Column(String(7), nullable=False, index=True)   # YYYY-MM
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    department = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=True)
    base_salary = Column(Float, nullable=False)
    working_hours = Column(Float, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True) 
    
    # Hierarchy fields
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    position_level = Column(String(50), nullable=True) # Top, Senior, Junior, etc.
    
    simulate_failure = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
    performance_reviews = relationship("PerformanceReview", foreign_keys="PerformanceReview.employee_id", back_populates="employee")
    authored_reviews = relationship("PerformanceReview", foreign_keys="PerformanceReview.manager_id", back_populates="manager_reviewer")
     
    __table_args__ = (
        UniqueConstraint("run_month", "email", name="uq_employee_run_month_email"),
    )   