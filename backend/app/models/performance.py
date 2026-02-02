from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    quarter = Column(Integer, nullable=False) # 1, 2, 3, 4
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=True) # 1.0 to 5.0
    feedback = Column(Text, nullable=True)
    ai_insights = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_reviews")
    manager_reviewer = relationship("Employee", foreign_keys=[manager_id], back_populates="authored_reviews")
