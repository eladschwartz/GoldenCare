
from typing import List
from fastapi import HTTPException, status, Depends, APIRouter, Response, Request
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(
     prefix="/departments",
     tags = ['Departments'],
     dependencies=[Depends(oauth2.get_current_user)],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.DepartmentOut)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    
    new_department = models.Department(**department.model_dump())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
     
    return new_department

@router.get("/all", response_model=List[schemas.DepartmentOut])
def get_departments(request:Request, db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()
    
    return departments

@router.get("/", name="departments", response_model=List[schemas.DepartmentOut])
def get_template_departments(request:Request, db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()
    
    return templates.TemplateResponse("dashboard/departments.html", {"request": request, "data": departments})

@router.get("/{id}", response_model=schemas.DepartmentOut)
def get_department(id: int, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == id).first()
    
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id: {id} doesn not exist")
    
    return department

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(id: int, db: Session = Depends(get_db)):
    department_query = db.query(models.Department).filter(models.Department.id == id)
    
    department = department_query.first()
    
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with id:{id} doesn't exist")
    
    #Check if role is admin
    
    department_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

