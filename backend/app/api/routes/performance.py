from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.models.performance import PerformanceReview
from backend.app.models.employee import Employee
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/performance", tags=["performance"])

class PerformanceReviewCreate(BaseModel):
    employee_id: int
    manager_id: int
    quarter: int
    year: int
    rating: float
    feedback: str
    ai_insights: dict = None

class PerformanceReviewResponse(PerformanceReviewCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/reviews/", response_model=PerformanceReviewResponse)
def create_review(review: PerformanceReviewCreate, db: Session = Depends(get_db)):
    db_review = PerformanceReview(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/reviews/{employee_id}", response_model=List[PerformanceReviewResponse])
def get_employee_reviews(employee_id: int, db: Session = Depends(get_db)):
    return db.query(PerformanceReview).filter(PerformanceReview.employee_id == employee_id).all()

@router.get("/reviews/manager/{manager_id}", response_model=List[PerformanceReviewResponse])
def get_manager_reviews(manager_id: int, db: Session = Depends(get_db)):
    return db.query(PerformanceReview).filter(PerformanceReview.manager_id == manager_id).all()

@router.get("/snapshots/{quarter}/{year}")
def get_performance_snapshots(quarter: int, year: int, db: Session = Depends(get_db)):
    # Logic to get all employees and their performance for a quarter
    employees = db.query(Employee).all()
    results = []
    for emp in employees:
        review = db.query(PerformanceReview).filter(
            PerformanceReview.employee_id == emp.id,
            PerformanceReview.quarter == quarter,
            PerformanceReview.year == year
        ).first()
        results.append({
            "employee_id": emp.id,
            "name": emp.name,
            "department": emp.department,
            "job_title": emp.job_title,
            "rating": review.rating if review else None,
            "status": "Completed" if review else "Pending"
        })
    return results
