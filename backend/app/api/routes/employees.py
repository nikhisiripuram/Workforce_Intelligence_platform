from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.models.employee import Employee
from pydantic import BaseModel

router = APIRouter(prefix="/employees", tags=["employees"])

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    department: str
    job_title: Optional[str]
    manager_id: Optional[int]
    position_level: Optional[str]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[EmployeeResponse])
def get_employees(
    run_month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db)
):
    query = db.query(Employee)
    if run_month:
        query = query.filter(Employee.run_month == run_month)
    return query.all()

@router.get("/org-tree")
def get_org_tree(
    run_month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db)
):
    query = db.query(Employee)
    if run_month:
        query = query.filter(Employee.run_month == run_month)
    employees = query.all()
    
    # Simple nested structure building
    emp_map = {emp.id: {
        "id": emp.id,
        "name": emp.name,
        "job_title": emp.job_title,
        "department": emp.department,
        "position_level": emp.position_level,
        "children": []
    } for emp in employees}
    
    roots = []
    for emp in employees:
        if emp.manager_id and emp.manager_id in emp_map:
            emp_map[emp.manager_id]["children"].append(emp_map[emp.id])
        else:
            # Only count as root if it's truly a top-level for this month
            # Or if the manager isn't in this specific month's run
            roots.append(emp_map[emp.id])
            
    return roots

@router.put("/{employee_id}/assign-manager")
def assign_manager(employee_id: int, manager_id: Optional[int], db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if manager_id:
        manager = db.query(Employee).filter(Employee.id == manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
            
    emp.manager_id = manager_id
    db.commit()
    return {"status": "success"}
